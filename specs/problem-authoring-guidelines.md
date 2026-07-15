# Problem authoring guidelines

The single source of truth for **what makes a lootcode problem good**. Where
`specs/problem-schema.md` defines the on-disk *format*, this file defines the
*quality bar* and the house rules every new problem must meet.

**This file is loaded by every problem-authoring path**, so a rule added here
takes effect everywhere at once:

- the `/add-problem` and `/new-problem-set` slash commands,
- the `problem-author` subagent,
- the **in-app AI generator** (`app/llm/generator.py`) — it injects the block
  between the `AI-GUIDELINES` markers below straight into the model's system
  prompt at generation time, so edits here change generated problems with no
  code change and no restart.

> **Owner:** add your house rules under [Custom requirements](#custom-requirements).
> Anything inside the marked block reaches the AI generator; anything outside it
> is guidance for humans and agents only.

<!-- AI-GUIDELINES:START -->
## Statement

- Open with the task in one or two sentences; bold the thing to return.
- Include a `## Constraints` section with concrete bounds — array lengths, value
  ranges, and any guarantees the solver may rely on (e.g. "exactly one valid
  answer exists", "the list is non-empty"). Bounds drive the test design.
- Give **2–3 worked `## Examples`**, each with `Input:`, `Output:`, and a short
  `Explanation:` when the mapping isn't obvious.
- If the answer may be returned **in any order**, or is a **set of groups** whose
  order is irrelevant, say so in prose **and** set the matching `compare` mode
  (below). The statement and the judge must never disagree.

## Compare mode (the judge must match the statement)

Set `meta.json.compare` to the weakest mode the statement actually promises:

- `exact` — order matters (scalars, sorted output, positional arrays, linked lists).
- `unordered` — the returned list is a multiset; top-level order ignored.
- `set_of_lists` — list of groups; neither the outer order nor each inner list's
  order matters (3Sum, Combination Sum, Group Anagrams).

If the prose says "any order" / "any valid answer" the mode must NOT be `exact`.
`scripts/audit.py` fails the build on a statement/judge mismatch, and also checks
that a deliberately re-ordered valid answer is still accepted.

## Tests

- **6–10 cases total**: a few **visible** (`hidden: false`, these double as the
  statement's examples) and several **hidden** (`hidden: true`).
- Cover, at minimum: the smallest valid input, the boundary of every constraint,
  and the awkward values the constraints allow — negatives, zero, duplicates,
  ties, empty/one-element collections.
- Include **at least one large input** sized so that a brute-force solution of
  the wrong complexity times out (or is clearly distinguished) while the intended
  solution stays comfortably within `timeLimitMs`.
- Put the tricky "gotcha" cases in **hidden** tests — solvers never see hidden
  input/expected/output, only pass/fail.
- Every test's `expected` must equal the canonical solution's output under the
  chosen `compare` mode. Inputs are keyed by parameter name.

## Solver contract

- Exactly one **top-level function** named `function.name`, no class wrapper.
- Use **camelCase** for the function name, LeetCode-style (e.g. `twoSum`,
  `maxProfit`), matching the existing bank.
- Parameters match the test-input keys by name. Return values must be
  JSON-serializable.
- **Binary trees:** declare a tree parameter/return as type `"TreeNode"`. Tests
  still encode the tree as a level-order array (`null` for a missing child; `[]`
  is the empty tree), but the solver receives/returns a real `TreeNode`
  (`value`, `left`, `right`; `TreeNode(value=None, left=None, right=None)`). The
  `TreeNode` class is provided automatically — never define it, and a `TreeNode`
  return is allowed even though it isn't JSON-serializable. Keep `compare` as
  `exact`.

## Canonical solution & starter

- `solution/solution.py` is **complete, correct, and passes every test** within
  the time/memory limits. Use the **Python standard library only** — the sandbox
  has no network and no third-party packages (see `docs/code-execution.md`).
- `starters/python/solution.py` is just the signature plus a short docstring or
  `pass` — never any solution logic.

## Difficulty & tags

- Keep `difficulty` honest relative to the existing problems in `content/problems/`.
- Tags MUST come from the **canonical vocabulary** (38 tags) — see
  `specs/tags.md` / `app/tags.py`. Pick 1–4 that describe the core
  technique/structure. Don't coin new tags or use near-synonyms (use
  `breadth-first-search` not `bfs`, `queue` not `monotonic-queue`); `math` is a
  catch-all umbrella, used only when nothing more specific fits. If a problem
  truly fits none, surface it rather than inventing a tag. (Writes are
  auto-normalized to canonical tags, so off-vocabulary tags are corrected/dropped.)

## Custom requirements

<!-- OWNER-EDITABLE. Add your house rules below. Everything in this AI-GUIDELINES
     block (these included) is injected into the in-app generator's system prompt,
     so keep entries short and imperative. Delete the examples once you've added
     your own. -->

- _(example — keep or replace)_ Solutions must rely only on the Python standard
  library; do not assume any third-party package is importable.
- _(example)_ Prefer fresh framings over verbatim copies of famous problems.
- **TODO(owner):** add your requirements here.

<!-- AI-GUIDELINES:END -->

## Figures (authoring-time only)

Some problems read far more clearly with a diagram (matrices, trees, graphs, grid
paths, intervals on a number line). Whether to add one, how to draw it (SVG), and
how it is stored and served live in **`docs/problem-images.md`** — the single
source of truth for figures. This is a Claude Code / `problem-author` step (the
in-app AI generator can't emit image assets), which is why it sits outside the
AI-GUIDELINES block above. The `bulk-import` skill applies the rubric on every
batch import.

## How these guidelines are enforced

Before a problem is considered done, both of these must be green:

```bash
python scripts/seed.py     # canonical solution passes ALL of its own tests
python scripts/audit.py    # statement ↔ compare ↔ fairness are consistent
```

When you add or edit test cases, also confirm every case input is **in-bounds**
for the stated constraints via the problem's input-constraint validator
(`content/problems/<slug>/input_validator/input_validator.py`):

```bash
python scripts/check_constraint_validators.py --slug <slug>   # each input must satisfy validate_input()
```

See `docs/input-validators.md`.

The in-app generator additionally runs every generated problem through the real
sandbox executor before returning it, and retries once if the reference solution
fails — but `seed.py`/`audit.py` remain the gate for anything written to
`content/problems/`.
