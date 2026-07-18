# Class-based ("design") problems

Most lootcode problems are one top-level function. **Design problems** (LeetCode's
"design" bucket: LRU Cache, Min Stack, Browser History, Trie, BST Iterator, …) ask
the solver to implement a **stateful class**, graded by replaying a sequence of
method calls against one instance and comparing the collected outputs.

This doc is the how-to. The on-disk format is specified in
`specs/problem-schema.md` ("Class-based (design) problems"); the quality bar is in
`specs/problem-authoring-guidelines.md`.

## How it runs

`kind: "class"` flows through the same path as function problems; only the
sandbox seam differs:

- **Schema** (`app/content.py`, `app/models.py`): a `class` block (name +
  constructor params + method list) instead of a `function` block. In the DB and
  the in-memory dict, `params` holds the constructor params, `class_name` the
  class, `class_methods` the method signatures; `function_name`/`return_type` are
  unused. A `kind` column (default `"function"`) discriminates.
- **Harness** (`app/executor/harness.py`): `main()` branches on
  `payload["kind"]`. `_run_class` instantiates `class_name(*ctor_args)` (output
  `null`), then for each later operation calls `getattr(instance, op)(*args)` and
  collects the return (`null` for `void`). The whole operation sequence runs under
  one per-test SIGALRM — a LeetCode-style overall time budget. Rich/helper-typed
  args are decoded and rich-typed returns encoded via `_CODECS`, per method.
- **Grading** (`app/executor/__init__.py`): unchanged. The collected outputs list
  is compared to `expected` with `_equal` under `compare` (`exact`).
- **Validation** (`scripts/test_llm_output.py`, `app/problem_validation.py`): a
  class-kind branch checks the canonical/starter define the class with a matching
  `__init__` + methods (static AST) and that each test is a well-formed operation
  sequence; then the canonical must pass every test in the sandbox.
- **UI** (`app/templates/problem.html`, `app/routers/pages.py`): the solve page
  shows the class name + a method-signature block; the admin New/Edit forms have a
  kind selector, a class-name field, and a class-methods JSON field.

## Injected helper types

Beyond `TreeNode`/`ListNode`, two param-only helper types are injected for design
problems (defined in `app/executor/harness.py`, displayed via
`app/routers/pages.py::PROVIDED_TYPE_DEFS`):

- `Iterator` / `Iterator<int>` — wraps a flat JSON array; exposes
  `hasNext()`/`next()`. (`peeking-iterator`)
- `List<NestedInteger>` / `NestedInteger[]` — a nested JSON list decoded to a list
  of `NestedInteger` (`isInteger()`/`getInteger()`/`getList()`).
  (`flatten-nested-list-iterator`)

Adding another helper type = one `_CODECS` entry + one `PROVIDED_TYPE_DEFS` entry
(+ an `executor-security-reviewer` pass on the harness change).

## Authoring one

1. **Statement** — stage the raw statement under a `<staging-dir>/<slug>/` (the
   staging folder name is arbitrary): a reduced `meta.json` with a `body` field +
   `problem.md`. The "Implement the `X` class:"
   bullet list gives the class name, constructor, and each method's signature and
   return type; the worked example gives the `operations`/`args`/`Output` arrays.
2. **Scaffold** — build a `content/problems/<slug>/` from the statement: a
   `meta.json` `class` block (name + constructor params + method signatures, mapping
   LeetCode's C-style type labels onto lootcode's — see `specs/problem-schema.md`),
   `problem.md`, a class starter stub, and the worked example as a visible test.
3. **Canonical** — write `solution/solution.py` implementing the class correctly.
   `python scripts/verify_bank.py <slug> -v` runs it against the tests.
4. **Hidden tests** — add edge/large operation sequences. Compute each expected
   outputs list by running the canonical (it is the only oracle). Keep
   `input = {"operations": [...], "args": [[...], ...]}`, `expected` a list of the
   same length.
5. **Tags / hints** — canonical tags only (`app/tags.py`); ≤3 progressive hints
   whose last tier hints at the insight, not the code.
6. **Verify** — `python scripts/seed.py` (canonical passes) and
   `python scripts/audit.py` (statement ↔ judge) must stay green.

The pilot `design-browser-history` is a worked reference end-to-end.

## Bulk-importing fully-generated problems

The scaffold above is for hand-authoring one problem from a bare statement. When a
batch has **already** been through the Mode-A generator — each `<staging-dir>/
<slug>/` carries a fully-populated `generated_full_problem.json` (contract +
`canonical_solution` + `tests` + `hints` + `tags`) next to `meta.json` (title +
`body`) and an optional `assets/` — the whole import is scripted (the staging
folder name is arbitrary; substitute your own):

```
python scripts/import_generated_problems.py <staging-dir> --dry-run   # verify, write nothing
python scripts/import_generated_problems.py <staging-dir>             # write clean ones
```

This is the **full gate** (same layout, both problem kinds): for each slug it runs
presence/slug → strict structural (`scripts/test_llm_output.py`) → slug-collision →
behavioral + statement↔judge consistency (`scripts/audit.py`), and only slugs that
pass **all** of them qualify. It then assembles a live `content/problems-extended/
<slug>/` (default `--out`): `problem.md` = `# <title>` + `body` (with `](assets/x)`
rewritten to the served `](/problems/<slug>/assets/x)` path), the schema
`meta.json` (class block, normalized canonical tags, hints, limits, scoring),
`tests/cases.json`, `starters/`, `solution/`, and the copied `assets/` — then
**reloads from disk, upserts the DB, and re-verifies from the DB**. A slug already
in another content root or the DB is a hard collision (reconcile manually); one in
the target root needs `--overwrite`. A `SKIP ... behavioral` row means the
canonical fails its own tests — hand that dir to the `design-problem-repair` agent,
then re-run. The `generated-problem-import` agent drives this whole loop (dry-run →
triage → repair/defer → import). Non-deterministic / compositional problems (below)
stay deferred and are expected to fail the gate. **Full reference:
`docs/importing-problems.md`.**

## Not yet supported (deferred)

Grading is exact-match on the outputs list, so two categories need a future
**custom judge** (`compare: "custom"` + a trusted per-problem checker) and are out
of scope today:

- **Non-deterministic** — a method returns a random/any-valid answer
  (`insert-delete-getrandom-o1`'s `getRandom`, `shuffle-an-array`). Needs a
  membership/permutation check, not equality.
- **Compositional** — the answer is graded by composing methods, with no fixed
  per-call output (`serialize`↔`deserialize`, `encode`↔`decode-tinyurl`). Needs a
  per-problem driver.

Also deferred: extending the in-app AI generator (`app/llm/generator.py`) to author
class problems.

## Hardening a design problem's tests

Class problems are first-class in the test-strengthening engine. Per-problem input
validators for class inputs are generated **deterministically** from the class block
(no LLM) by `scripts/generate_class_validators.py` — a `validate_input(operations,
args)` that checks the sequence is well-formed (aligned lists, constructor once at
the front, declared methods, per-arg arity/type). To widen a suite:

```bash
python scripts/generate_class_validators.py --slug <slug>    # fairness gate (once)
python scripts/oracle.py cover <slug>                        # coverage-widening cases
python scripts/oracle.py cover <slug> --no-stress --apply    # ...write them
python scripts/oracle.py fuzz <slug> --solution bad.py       # add cases a known-bad class fails
```

`scripts/strengthen_tests.py <slug> [-j N]` is the batch form. Grading is
sandbox-only and coverage-driven (operation-sequence features + output signature);
mutants are off by default for class. See `docs/test-strengthening.md`, "Class/design
problems".
