.PHONY: install seed dev run test docker

install:        ## create venv and install dev deps
	python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -r requirements-dev.txt

seed:           ## load content into the DB and verify canonical solutions
	.venv/bin/python scripts/seed.py

dev:            ## run the dev server with autoreload (localhost)
	.venv/bin/uvicorn app.main:app --reload

run:            ## run the server bound to the LAN (HOST=0.0.0.0)
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

test:           ## run the test suite
	.venv/bin/python -m pytest -q

docker:         ## build and run via docker compose
	docker compose up --build
