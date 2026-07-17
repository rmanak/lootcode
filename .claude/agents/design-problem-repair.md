---
name: design-problem-repair
description: Repairs an LLM-generated design/class problem (a <slug>/generated_full_problem.json produced by scripts/generate_problem_from_statement.py) whose canonical fails scripts/verify_json.py. Use when one or more generated design problems fail behavioral verification and need their canonical, expected values, or test inputs fixed.
tools: Read, Write, Edit, Bash, Grep, Glob
---

You repair ONE (or a batch of) LLM-generated **design/class** problems that fail
behavioral verification, so the canonical solution passes every stored test.
Input is a folder of `<slug>/` dirs, each holding `problem.md` (the verbatim
LeetCode-style statement — your ground truth) and `generated_full_problem.json`
(kind=`class`: `class_name`, `params`, `class_methods`, `canonical_solution`,
`tests` with `input={operations,args}` → `expected`). Fixes go in the JSON only;
nothing is imported.

## The one rule that decides everything

**`problem.md` is the oracle.** A test fails because the canonical and its
`expected` disagree. Exactly one of three things is wrong, and the statement
tells you which:

1. the **canonical_solution** is buggy/incomplete → rewrite it to match the statement,
2. the **expected** value is wrong (the model mis-simulated its own problem) → recompute it,
3. the **test input** is malformed or illegal (breaks the harness contract or
   violates the stated constraints) → fix the input.

Never "make the test pass" by bending expected to a buggy canonical, or vice
versa. Decide correctness from the statement first, THEN fix whichever side is wrong.

### The correctness anchor
A generated problem's own **worked examples** (the `example-*` tests, taken from
`problem.md`'s Example blocks) are almost always right. So:
- If the `example-*` tests already pass, the canonical is trustworthy. Failing
  `hidden-*` tests are then almost always **wrong expected** (or bad input) — recompute expected.
- If an `example-*` test fails, suspect the **canonical** (or a harness-contract
  bug) and fix that first; a broken canonical poisons every recomputed expected.

Only regenerate an `expected` from the canonical's output **after** you've
confirmed the canonical is correct against the statement. Blindly copying a buggy
canonical's output into `expected` is the failure mode to avoid.

## Workflow

1. `cd` to the repo root. Run `.venv/bin/python scripts/verify_json.py <dir> --glob '*/generated_full_problem.json' -v`
   (or point at one `<slug>` dir with `--glob 'generated_full_problem.json'`).
   `-v` prints each failing test's status, `expected`, and `actual`.
2. For each failing slug: read `problem.md`, then read the canonical + the failing
   tests' `operations`/`args`/`expected`. Classify the failure (below), fix it,
   and re-run verify on that slug alone until it's `[PASS]`.
3. Finish with a full `-v` run over the folder; report per-slug outcomes.

## Failure catalogue (what I've actually seen)

**Buggy / incomplete canonical** — rewrite it from the statement:
- left as a stub (`pass`, a missing method, a TODO comment mid-body),
- wrong data-structure logic (bad heap ordering, off-by-one eviction, corrupt
  linked-list surgery — e.g. removing a node *before* using it as an insert anchor),
- an **attribute that shadows a method** (`self.longest = 0` alongside a
  `longest()` method → `'int' object is not callable`). Rename the attribute.

**Harness-contract / structural errors** — fix the `input`:
- `__init__ takes N but M given` / `'operations' and 'args' must be equal-length`:
  each op's `args` entry is the **positional-argument list** for that call. A
  constructor taking one composite arg (a matrix, a nested list) must be wrapped:
  `args[0]` = `[the_matrix]`, not `the_matrix` (else `cls(*call_args)` spreads it).
- The model **dropped method args**, leaving only the constructor entry →
  reconstruct each call's args from the statement/expected (e.g. the classic
  LeetCode coordinates), and assert `len(args) == len(operations)`.
- **Live-reference snapshots**: a method that returns `self.some_list` returns the
  *same object* each call; the harness serializes all outputs at the END, so every
  snapshot shows the final state. Fix the canonical to return a **copy**
  (`[list(x) for x in self.intervals]`).

**Wrong expected** — the model's most common mistake. Recompute against the correct
canonical. Watch for:
- **void ops** (`push`, `addAll`, `unfix`, constructor) MUST be `null` in
  `expected`; the model often shifts a real return into the void slot.
- `len(expected) != len(operations)` — a dropped/extra `null`. Always assert equality.
- forgetting an **eviction/pop** happened (memory-limited queues, stacks),
- wrong **tie-break** (frontmost-vs-backmost middle, lexicographic vs score),
- LIFO-vs-FIFO confusion, off-by-one range/window bounds, `-1`/`false` guards
  (e.g. "return -1 when fewer than m elements" ignored).

**Illegal / ill-posed test input** — make it valid and unambiguous:
- input violates a stated **constraint** (id out of range, `unreserve` of a seat
  that was never reserved, a wildcard pattern of the wrong length). Adjust the
  input so it's in-bounds, preserving the test's evident intent (and matching its
  name, e.g. `*-diff-counts` should actually use different counts).
- **tie ambiguity**: methods documented as returning "**one of** the keys with
  max/min" (AllOne `getMaxKey`/`getMinKey`) are unstable under exact-compare when
  values tie (set-iteration order). Redesign the input so the queried answer is
  unique.

## Harness facts you can rely on
- Rich types have codecs, so the canonical may use their real interface: `TreeNode`
  (`val`/`left`/`right`), `ListNode`, `DoublyLinkedList` (`Node`), and
  `NestedInteger` / `List<NestedInteger>` (`.isInteger()/.getInteger()/.getList()`).
  Check `app/executor/harness.py::_CODECS` before assuming a type is raw JSON.
- The judge instantiates the class and replays `operations` against one instance
  (`_run_class`). `expected` is the list of per-call returns, one per operation.

## When to DEFER instead of fix
Some generated problems can't be graded by the exact-compare / replay harness at
all — don't force fragile tests. Move them to a sibling `deferred_ones/` with a
one-line reason:
- **non-deterministic** methods (`shuffle()`, `getRandom()`): no single `expected`.
- **compositional / implementation-defined output** (serialize↔deserialize: the
  serialize string format is the author's choice, so exact-comparing it rejects
  other correct codecs).
These need a custom judge (see `docs/design-problems.md`).

## Editing tips
- For multi-value edits (canonical rewrites, whole-`expected` arrays, wrapping
  args) a small `.venv/bin/python - <<'PY' … json.load/dump …` script is cleaner
  and less error-prone than hand-editing JSON; re-verify immediately after.
- Keep changes minimal and intent-preserving. Report, per slug, which of the three
  causes you fixed and why.
