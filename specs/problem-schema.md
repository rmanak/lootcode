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
└── solution/
    └── solution.py             # canonical reference solution (must pass all tests)
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
Return values must be JSON-serializable.

## `meta.json`

```jsonc
{
  "slug": "two-sum",
  "title": "Two Sum",
  "difficulty": "easy",               // easy | medium | hard
  "tags": ["array", "hash-table"],    // topics, used for filtering
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
`int[]`, `int[][]`, …); values are passed through as plain JSON.

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

## The canonical solution

`solution/solution.py` is a complete, correct solution. `python scripts/seed.py`
runs it against the problem's own tests and flags any problem whose canonical
solution doesn't pass everything — keep it green.

## Checklist before publishing

- [ ] `meta.json` is valid; `starters/python/solution.py` exists.
- [ ] `solution/solution.py` passes **all** tests (`python scripts/seed.py`).
- [ ] Hidden cases cover edge/large inputs.
- [ ] Difficulty and tags are honest.
