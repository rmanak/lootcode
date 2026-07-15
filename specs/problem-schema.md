# Problem authoring spec

How a coding problem is defined on disk. The canonical example is
`content/problems/two-sum/`. The `problem-author` subagent, the
`/add-problem` command, and the Admin UI all follow this.

> This file is the **format**. For the **quality bar and house rules** every new
> problem must meet (and the owner's custom requirements that also feed the in-app
> AI generator), see `specs/problem-authoring-guidelines.md`.

> **V1 is Python-only.** The schema keeps a `languages` list for the future, but
> only `python` is wired up today.

## Directory layout

```
content/problems/<slug>/
├── problem.md                  # statement (Markdown)
├── meta.json                   # metadata (below)
├── tests/
│   └── cases.json              # test cases (visible + hidden)
├── starters/
│   └── python/solution.py      # starter stub shown in the editor
├── solution/
│   └── solution.py             # canonical reference solution (must pass all tests)
└── input_validator/
    └── input_validator.py      # validate_input(...) predicate for legal inputs (see below)
```

`<slug>` is kebab-case, unique, and matches `meta.json.slug`.

## Solver contract

The solver defines a **top-level function** named `meta.function.name` that takes
exactly the listed parameters by name — **no class wrapper**:

```python
def twoSum(nums, target):
    ...
```

The harness calls it once per test as `twoSum(**input)` and compares the return
value to the test's `expected` using the problem's `compare` mode (see below).
Return values must be JSON-serializable — **except** for parameters/returns
declared as a rich type (see "Rich types" below), where the harness converts
between the JSON wire form and a real object for you.

## `meta.json`

```jsonc
{
  "slug": "two-sum",
  "title": "Two Sum",
  "difficulty": "easy",               // easy | medium | hard
  "tags": ["array", "hash-table"],    // topics, used for filtering
  "hints": [                          // OPTIONAL: 0–3 progressive hints (see below)
    "Can you use the fact that lookups in a set are O(1)?"
  ],
  "languages": ["python"],
  "limits": { "timeLimitMs": 10000, "memoryLimitMb": 512 },
  "function": {
    "name": "twoSum",
    "params": [
      { "name": "nums", "type": "int[]" },
      { "name": "target", "type": "int" }
    ],
    "returns": { "type": "int[]" }
  },
  "scoring": { "type": "weighted", "points": 100 },
  "compare": "exact"                  // exact | unordered | set_of_lists
}
```

`type` strings are documentation for the author (`int`, `string`, `bool`,
`int[]`, `int[][]`, …); values are passed through as plain JSON — **with one
exception**: a small set of *rich types* (see below) are load-bearing and tell
the harness to build/serialize a real object at the sandbox boundary.

### Rich types (`TreeNode`, `ListNode`, `DoublyLinkedList`)

A parameter or return may be declared with a rich type. The **on-disk test format
stays a plain JSON value**; the harness decodes it into a real object before
calling the solver, and encodes a returned object back into that JSON form before
grading. Comparison still happens on the JSON form in the trusted parent, so
`compare` stays `exact` and `tests/cases.json` needs no special format. The class
is **injected automatically** into the solution's namespace — do not define it
yourself — and the "JSON-serializable return" rule is waived for a rich-type
return. The codecs live in `app/executor/harness.py` (`_CODECS`); adding another
rich type means adding an entry there.

| Type | Injected class | Wire form (on disk & compared) | Reference problems |
|------|----------------|-------------------------------|--------------------|
| `TreeNode` | `TreeNode(value=None, left=None, right=None)` | LeetCode **level-order array** with `null` holes, e.g. `[3,9,20,null,null,15,7]` (`[]` = empty tree; trailing `null`s trimmed on return) | `invert-binary-tree`, `maximum-depth-of-binary-tree`, `same-tree` |
| `ListNode` | `ListNode(val=0, next=None)` | flat array of the node values in order, e.g. `[1,2,3]` (`[]` = empty list) | `reverse-linked-list`, `merge-two-sorted-lists`, `add-two-numbers`, `reverse-nodes-in-k-group` |
| `DoublyLinkedList` | `Node(val=0, prev=None, next=None)` | flat array of the node values in order (the harness wires both `.prev` and `.next` on decode) | *(infra ready; no bank problem uses it yet)* |

**Limitations (same for every rich type today):** the codec matches the **whole**
declared type, so only a *top-level* rich type is decoded — a nested one like
`ListNode[]` (e.g. `merge-k-sorted-lists`, `split-linked-list-in-parts`) is not,
and stays in array form. Decoding is also strictly **per-parameter**: a problem
that reconstructs structure by combining params (e.g. `linked-list-cycle`, which
builds a cycle from `head` + `pos`) can't use a rich type and stays in array form.
A single problem *may* mix rich types across params (e.g. `linked-list-in-binary-tree`
takes `head: ListNode` **and** `root: TreeNode`).

### `hints` (optional)

A problem may carry **up to 3** hints — short, progressive nudges shown on the
problem page as collapsible "Hint 1 … Hint N" panels **below the Topics section**,
each **collapsed by default** (a solver opts in by expanding one). Order them
**most general first, most revealing last** so a stuck solver can peek at just one.

**Each tier has a different job**, and the last tier must stop short of the answer:

- **Hint 1** — a light conceptual nudge: reframe the problem or point out what to
  notice. Names no technique; gives almost nothing away.
- **Hint 2** — names the key technique / data structure / subproblem ("a stack",
  "two pointers", "a DP over prefixes"). Naming the technique here is correct.
- **Hint 3** — the crucial **insight**, not the mechanics: what the DP state means,
  why the technique works, the key observation, the base/edge case to watch. It may
  be genuinely helpful but must **not** state the recurrence/transition, a formula,
  code/pseudocode, literal index expressions (`dp[i][j] = …`), or a step-by-step
  recipe. Reveal the idea; leave the derivation and the code to the solver.

The single most common quality failure is a hint 3 that transcribes the solution
(e.g. "for each amount, take the min previous result plus one" *is* the recurrence).
Hints are generated and quality-gated by the pipeline in `docs/hint-generation.md`;
run `python scripts/improve_hints.py audit` to check a problem's hints, or `fix` to
regenerate weak ones.

- Shape: a JSON array of plain-text strings, e.g.
  `"hints": ["Think about a hash map.", "What is the complement of each value?"]`.
- **Optional and back-compatible:** omit the key (or use `[]`) for no hints — the
  section simply doesn't render. Everything works with or without it.
- The loader trims blank entries and **caps the list at 3** (`normalize_hints` in
  `app/content.py`, `MAX_HINTS`); extras are dropped, so authoring 4+ is a no-op.
- Rendered as plain text (no Markdown), so avoid relying on `*`/`_`/backtick
  formatting; write hints as ordinary prose. Only render N panels for N hints
  (1 hint → just "Hint 1").
- Admin UI: the add/edit forms expose a "Hints (one per line, max 3)" textarea;
  hints round-trip through `meta.json` (written back only when non-empty).

### `compare` — how the judge matches the returned value to `expected`

The statement and the judge **must agree**. Pick the mode that matches what the
statement promises:

| mode | meaning | use when the statement… |
|------|---------|--------------------------|
| `exact` (default) | structural equality; order matters | requires a specific order, or returns a scalar / a sequence whose order is meaningful (sorted lists, linked-list order, positional arrays). |
| `unordered` | the returned **list** is a multiset (top-level order ignored; elements compared exactly) | says the elements may be returned **in any order** — e.g. Two Sum's index pair, "return the cells in any order". |
| `set_of_lists` | list of lists; outer order **and** each inner list's order are ignored | the answer is a collection of groups/tuples where neither the group order nor the order within a group matters — e.g. 3Sum, Combination Sum, Group Anagrams. |

> If the answer is genuinely non-unique (e.g. "return *any* longest palindrome"),
> either pin it in the statement (e.g. "the one starting at the smallest index")
> so `exact` is fair, or add a comparison mode that captures the equivalence.
> `python scripts/audit.py` flags any statement that promises "any order" while
> the judge is still `exact`.

## `tests/cases.json`

```jsonc
{
  "cases": [
    { "name": "example-1",
      "input": { "nums": [2, 7, 11, 15], "target": 9 },  // keys == param names
      "expected": [0, 1],
      "weight": 1,        // weighted scoring: score = points * passed_weight / total_weight
      "hidden": false }   // false = shown as an example; true = used on run but never revealed
  ]
}
```

Rules:
- A few **visible** cases (examples) and several **hidden** ones, incl. edge and
  larger inputs.
- The platform runs **all** tests on every Run; hidden cases contribute to the
  score but only their pass/fail is shown — never their input/expected/output.

## `input_validator/input_validator.py`

Each problem carries an **input-constraint validator** exposing

```python
def validate_input(<params>) -> bool:   # params == meta.json function.params, by name
```

which returns `True` iff its arguments satisfy the input constraints the
statement promises (value ranges, lengths, shapes, character sets, structural
invariants). **When you add a new `(input, expected)` case, run its input through
`validate_input` first** — if it returns `False`, the input is out-of-bounds for
the problem and must not be added as a case. Check a problem (or the whole bank)
with:

```bash
python scripts/check_constraint_validators.py --slug <slug>   # every stored input must pass
```

Full reference — the contract, rich-type (`TreeNode`) handling, and how to
generate/regenerate a validator — is in `docs/input-validators.md`.

## The canonical solution

`solution/solution.py` is a complete, correct solution. `python scripts/seed.py`
runs it against the problem's own tests and flags any problem whose canonical
solution doesn't pass everything — keep it green.

## Checklist before publishing

- [ ] `meta.json` is valid; `starters/python/solution.py` exists.
- [ ] `solution/solution.py` passes **all** tests (`python scripts/seed.py`).
- [ ] Hidden cases cover edge/large inputs.
- [ ] Every case input is in-bounds (`python scripts/check_constraint_validators.py --slug <slug>`).
- [ ] Difficulty and tags are honest.
