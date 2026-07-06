# Importing a problem collection

`scripts/import_collection.py` validates and bulk-imports a **staged collection**
of ready-made problems into the bank in one shot. It is the safe, repeatable path
for adding many problems at once: it runs every guardrail the project already has
and **imports only the problems that pass all of them**, so you can run it
unattended without risking a broken or unfair problem entering the bank.

```bash
python scripts/import_collection.py <dir> --dry-run   # validate + report, write nothing (do this first)
python scripts/import_collection.py <dir>             # validate, then prompt before importing
```

## Input layout

A collection directory splits each problem's **statement** from its runnable
**core**, keyed by a shared `<slug>`:

```
<dir>/
├── statements/<slug>/problem.md   # the statement (Markdown), imported verbatim
├── statements/<slug>/meta.json    # ONLY its "title" is read; everything else ignored
├── statements/<slug>/assets/…     # OPTIONAL: figures (jpg/png/svg) the statement references
└── rest/<slug>.json               # the runnable "core" (see below)
```

`rest/<slug>.json` is exactly the LLM **core contract** (`specs/problem-schema.md`,
`docs/problem-generation.md`) — the same shape `scripts/test_llm_output.py`
validates and `app/llm/generator.py` emits:

```jsonc
{
  "difficulty": "medium",              // easy | medium | hard
  "tags": ["array", "two-pointers"],
  "function_name": "fourSum",
  "params": [{ "name": "nums", "type": "int[]" }, { "name": "target", "type": "int" }],
  "return_type": "int[][]",
  "compare": "set_of_lists",           // exact | unordered | set_of_lists
  "starter_code": "def fourSum(nums, target):\n    ...",
  "canonical_solution": "def fourSum(nums, target):\n    ...",
  "tests": [{ "name": "...", "input": {...}, "expected": ..., "weight": 1, "hidden": false }],
  "hints": ["...", "..."]              // OPTIONAL, up to 3 (see below)
}
```

The title and statement live outside `rest/` on purpose: the model that produced
the core never has to re-emit (and risk drifting from) the statement.

## What it checks (reuses existing gates — nothing re-implemented)

Per slug, cheapest → most expensive, stopping at the first failure so untrusted
code never runs for an already-broken problem:

1. **Presence & pairing** — all three files exist, valid JSON, non-empty `title`,
   non-empty `problem.md`, kebab-case slug that matches on both sides.
2. **Structural** — `scripts/test_llm_output.py` (strict pydantic + AST): required
   fields present and well-typed, valid function/param identifiers, `starter`/
   `canonical` parse and define the declared signature, each test's `input` keys
   equal the params, `expected` shape matches `compare`, ≥1 visible + ≥1 hidden
   test, JSON-serializable values.
3. **Slug collision** — see *Duplicate detection* below.
4. **Behavioral** — the canonical solution must pass **all** its own tests in the
   real sandbox (`app.executor.run_submission`, via `scripts/audit.py`).
5. **Statement ↔ judge consistency** — `scripts/audit.py`: a statement promising
   "any order" must not use `compare=exact`, and for relaxed modes a deliberately
   re-ordered valid answer must still be accepted (fairness).

Only slugs that clear **all** of these qualify. The script prints a report,
asks to confirm (unless `-y`), then imports each qualifying problem the durable
way: writes `content/problems/<slug>/` (the human-editable mirror), copies binary
figures, upserts the DB, and **re-verifies once more from the DB**.

## Tags (advisory — never block an import)

Non-canonical tags do not disqualify a problem. On write, `app/tags.py`'s
`normalize_tags` folds known aliases (e.g. `bfs` → `breadth-first-search`,
`intervals` → `sorting`) and drops meta-tags. A tag that is **neither canonical
nor a known alias** (e.g. `interval`) is *not* folded — it persists on disk
as-is, and the importer reports it as a warning:

```
· warn: non-canonical tag(s) ['interval'] not in vocabulary — will persist as-is (see specs/tags.md)
```

Fix these after import by editing the tag, or by folding it into the canonical
vocabulary in `app/tags.py` / `specs/tags.md` (don't invent tags inline — see the
`canonical-tags` skill).

## Hints (optional)

If `rest/<slug>.json` includes a `hints` array, the importer lifts it out before
the strict core validation (which forbids unknown keys), normalizes it
(`content.normalize_hints`: trims blanks, **caps at 3**), and writes it into
`meta.json`. A malformed `hints` value (not a list/string) is warned about and
ignored rather than failing the import. No `hints` key ⇒ the problem simply has
none. The `hints` column in the report shows how many were picked up.

## Figures

Statements may reference images with relative markdown `![alt](assets/<file>)`.
On import the files in `statements/<slug>/assets/` are copied (binary-safe) into
`content/problems/<slug>/assets/`, and the refs are rewritten to the served URL
`/problems/<slug>/assets/<file>` — the same convention existing problems use
(`docs/problem-images.md`). A referenced file that's missing is warned about.

## Duplicate detection

The **only** implemented duplicate signal is an **exact slug collision** against
both `content/problems/` and the DB. A collision is the cheapest, most concrete
signal of a genuine duplicate, so by policy the importer **skips it — it never
silently overwrites** an existing problem (`docs/problem-generation.md`):

```
· slug already exists in content/ or DB — possible duplicate; skipped (use --overwrite to replace deliberately)
```

Pass `--overwrite` to make replacement a deliberate, chosen action.

Broader **near-duplicate** detection — a problem imported under a *different*
slug that is a rephrasing or a reduction-equivalent of an existing one (e.g.
climbing-stairs ↔ compositions of {1,2}) — is **designed but not built**
(`docs/duplicate-detection-plan.md`, status: proposed). There is no `app/dedup.py`
yet, so the importer cannot catch those. When that lands, add it as a gate here
(right after the slug-collision check).

## Flags & exit status

| flag | effect |
|------|--------|
| `--dry-run` | run every check and print the report, but write/import nothing |
| `-y`, `--yes` | skip the confirmation prompt (import everything that qualifies) |
| `--overwrite` | deliberately replace a problem whose slug already exists |
| `--strict` | treat structural **warnings** as disqualifying too |
| `-v`, `--verbose` | print per-test / per-error detail under each skipped row |

Exit `0` only when the run is clean — everything qualified and (unless
`--dry-run`) imported. Exit `1` if any slug was skipped or an import failed to
re-verify (so a scripted/CI caller notices), and `2` on a usage/layout error.
Note: a run that successfully imports 54 of 59 still exits `1` because 5 were
skipped — read the printed summary, not just the code.
