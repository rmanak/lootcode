# lootcode — developer entry points.  `make help` lists them.
#
# Everything runs out of the project-local venv at ./.venv so a target never
# depends on what happens to be on PATH.
PY      := .venv/bin/python
PIP     := .venv/bin/pip
HOST    ?= 10.8.0.1
PORT    ?= 8000
# Worker threads for the bank-wide checks. Each unit of work is its own sandbox
# subprocess, so this scales with cores rather than with the GIL.
JOBS    ?= $(shell nproc 2>/dev/null || echo 8)

.PHONY: help install hooks seed dev run test test-fast test-cov lint lint-fix \
        format typecheck audit verify validators check check-bank docker clean

help:           ## list the targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk -F':.*?## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:        ## create ./.venv and install dev deps (pinned by constraints.txt)
	python3 -m venv .venv && $(PIP) install -U pip \
	  && $(PIP) install -r requirements-dev.txt -c constraints.txt

hooks:          ## install the pre-commit git hooks
	.venv/bin/pre-commit install

seed:           ## load content into the DB and verify canonical solutions
	$(PY) scripts/seed.py -j $(JOBS)

dev:            ## run the dev server with autoreload (localhost only)
	.venv/bin/uvicorn app.main:app --reload

# A non-loopback bind needs LOOTCODE_TRUST_LAN=1 — the app has no auth, so
# exposing it has to be a decision. Put it in .env or the environment; this
# target deliberately does not set it for you. See docs/security.md.
run:            ## run the server bound to $(HOST) (default 0.0.0.0 — the LAN)
	.venv/bin/uvicorn app.main:app --host $(HOST) --port $(PORT)

# --- checks ---------------------------------------------------------------
test:           ## run the whole test suite
	$(PY) -m pytest

test-fast:      ## run everything except the sandbox tier (no real subprocesses)
	$(PY) -m pytest -m "not slow"

test-cov:       ## run the suite with a coverage report
	$(PY) -m pytest --cov --cov-report=term-missing

lint:           ## ruff check (no writes)
	.venv/bin/ruff check .

lint-fix:       ## ruff check --fix
	.venv/bin/ruff check --fix .

format:         ## ruff format — OPT-IN, not part of `check`. See .pre-commit-config.yaml.
	.venv/bin/ruff format .

typecheck:      ## mypy over app/ + authoring/
	.venv/bin/mypy

audit:          ## statement <-> test <-> judge consistency over the bank
	$(PY) scripts/audit.py -j $(JOBS)

verify:         ## run every problem's canonical solution against its own tests
	$(PY) scripts/verify_bank.py -j $(JOBS)

validators:     ## assert every stored test input satisfies its validate_input()
	$(PY) scripts/check_constraint_validators.py

# The gate.
#
# `check` used to chain the seven targets above, which ran the bank's 1,173
# canonical solutions through the sandbox THREE times — serially in `seed`
# (37s), serially again in `audit` (35s), and in parallel in `verify` (6s).
# 93s of which 72 was duplicated work.
#
# So: `verify` is the one authoritative canonical run, and the other two skip
# what it covers. `seed --no-verify` still seeds (that is what `audit` reads);
# `audit --skip-canonical` still does everything unique to it — the statement
# <-> compare-mode consistency check and the re-ordered-answer fairness check.
# Run plain `make seed` / `make audit` for the standalone, self-contained
# versions; both take -j and are parallel by default now.
#
# Two phases, cheapest first, so a typo fails in seconds rather than minutes.
# Phase 2 runs the test suite concurrently with the bank checks: they share
# nothing (tests use a temp DB, the bank checks use content/ and lootcode.db).
check:  ## everything (deduplicated + parallel); serial output with -j1
	@$(MAKE) --no-print-directory lint typecheck
	@$(MAKE) --no-print-directory -j2 test check-bank

check-bank:     ## the bank half of `check`: seed -> audit -> verify -> validators
	@$(PY) scripts/seed.py --no-verify
	@$(PY) scripts/audit.py --skip-canonical -q
	@$(PY) scripts/verify_bank.py -j $(JOBS) -q
	@$(PY) scripts/check_constraint_validators.py

# --- misc -----------------------------------------------------------------
docker:         ## build and run via docker compose
	docker compose up --build

clean:          ## drop caches (not the DB, not content/)
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	find app scripts tests -name __pycache__ -type d -prune -exec rm -rf {} +
