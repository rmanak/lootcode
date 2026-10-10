# Authoring an ICF problem

A problem is a directory under `icf/problems/<slug>/`. Nothing is seeded into
a database: the loader reads it off disk (cached by mtime), so an edit shows
up on the next request.

```
icf/problems/<slug>/
  meta.json                        the contract
  problem.md                       shared scenario, data model, global rules
  levels/level1.md … level4.md     per-level requirements, prose + examples
  starter/solution.py              the template class — methods declared, bodies `pass`
  solution/solution.py             the canonical (never served to a solver)
  solution/level1.py … level3.py   optional per-level checkpoints
  tests/level1/visible.py          cases the solver sees in full
  tests/level1/hidden.py           cases the solver only sees pass/fail for
  …                                the same pair for levels 2, 3 and 4
```

## meta.json

```json
{
  "slug": "in-memory-database",
  "title": "In-Memory Database",
  "difficulty": "medium",
  "blurb": "One sentence for the card on /icf.",
  "tags": ["hash-map", "design"],
  "class_name": "Database",
  "time_cap_minutes": 90,
  "case_time_limit_ms": 4000,
  "levels": [
    {"level": 1, "title": "Records and fields", "points": 25,
     "methods": ["def set(self, timestamp: int, key: str) -> None: ..."]}
  ]
}
```

`methods` is what the workspace shows as the class signature, and the
validator checks each name against the starter — declare a method at the level
that introduces it.

Slugs are lower-case-kebab, and `static`, `attempts` and `api` are reserved
(they are routes).

## Writing the statements

`problem.md` and `levels/level<N>.md` are what a candidate reads for 90
minutes, so they get real prose. The notes in `icf.txt` are shorthand, not a
model: never copy their wording or clipped style. **`banking-system` is the
reference** — match its structure and tone. Rewriting an existing statement
follows the same rules, and never changes what the tests grade.

**`problem.md`, the Overview tab**

1. `### Instructions`: start with *"Your task is to implement a simplified
   version of a <system>."* Then, in plain English, say what the system is, who
   uses it and what it is for (*a bank keeps accounts that hold money:
   customers open an account, put money into it…*). After that, one paragraph
   on how levels unlock.
2. `### Requirements`: *"Implement the class `X`. Plan your design according to
   the level specifications below:"*, then one bullet per level, each written
   as *"Level N: The <system> should support …"*. End with the gating sentence:
   pass every visible and hidden test, and earlier levels are re-run.
3. `### The data model`, if there is one: the entities, in words, with one
   small literal example.
4. `### Notes`: rules that hold at every level (timestamps and their units,
   what values may be empty, no validation needed, a fresh instance is empty).

**`levels/level<N>.md`**

1. **Open with the feature and why someone wants it**, in one or two plain
   sentences: *"Initially, the banking system does not contain any accounts, so
   implement operations to allow account creation, deposits, and transfers
   between different accounts."* / *"The bank wants to identify people who are
   not keeping money in their accounts, so…"*. Never start with a method name.
2. **One block per method**: the full signature, with `self` and types, in a
   fenced `python` block. Below it, a sentence beginning *"should …"* that says
   what the method does, then its results, one condition per line: *"Returns
   `None` if `account_id` doesn't exist."* Say what a rejected call changes
   (normally nothing).
3. **Changes to earlier methods get their own list** (*"How the existing
   operations change"*). Never leave a candidate to infer them from an example.
4. **Define every term the first time it appears**: TTL, half-open intervals,
   "lexicographic", units (*24 * 60 * 60 * 1000 = 86400000 milliseconds*),
   rounding.
5. **`### Examples`**: *"The example below shows how these operations should
   work:"*, then a two-column `| Query | Explanation |` table. Every call gets
   its own row, and every row that returns something says
   ``returns `<value>` ``. Show ``database state: `{…}` `` or
   ``balances: `{…}` `` after
   the writes that matter. Explain every surprising `None`/`False` (*"returns
   `None`; alice only has 300, so nothing changes"*). Timestamps must strictly
   increase, just like in the tests.
6. **Every rule a test enforces belongs in the prose.** Read the `@case` labels
   of both `visible.py` and `hidden.py` and make sure each one is stated. A
   hidden test on an unstated rule is a trick question.
7. **Describe behaviour, not the data structure.** `docs/design.md` explains
   why: the level-1 modelling choice is what the format tests.
8. **Example values come from the canonical and are never worked out by
   hand.** Run each table against `solution/solution.py` before you commit.
   The problem's return values, state and expiry claims have to match it
   exactly.
9. Account and user names in examples are ids. Refer to them as *the account*
   or *its*, never *he* or *she*.

## From a brief to a statement

Briefs arrive in two registers. **Crib notes** (`icf.txt`, `inventory.txt`)
list the operations and little else. **Real CodeSignal statements** copied
from the web (`banking.txt`, `inmem.txt`, `cloud_storage.txt`) are the voice
the finished problem should have. Either way, the brief supplies the
requirements, and you supply everything below.

- **Reuse good source sentences.** CodeSignal patterns worth keeping:
  *"should …; Returns `X` if …, or `None` otherwise"*, *"The operation fails
  if …"*, *"It is guaranteed that …"* for inputs the tests never send,
  *"Note that …"* for a consequence that crosses levels, and *"sorted in
  descending order of … or, in the case of ties, …"*. Keep the source's own
  motivating sentence for each level whenever it has one.
- **Translate the API.** Java `camelCase`, `Optional<Integer>`, `"true"` and
  `""` become Python `snake_case`, `int | None`, `True`/`False` and `None`.
  Keep the source's method names otherwise (`find_file`, not `search`).
- **Close every gap in writing, never only in the canonical.** Briefs cover
  the happy path and one or two failures. For each method, ask: unknown id?
  name already taken? limit reached exactly? a call on itself (a copy onto the
  same name)? what does a rejected call change? how does the special user
  (`"admin"`) behave? does a derived object (a copy, a compressed file) count
  against limits and keep its owner? Each answer becomes a *"Returns `None`
  if …"* line when it is worth testing, or an *"It is guaranteed that …"* line
  when it would only add noise.
- **Web copies are damaged, so repair them deliberately.** Expect truncated
  example cells, explanation columns shifted against their queries, one token
  spelled two ways (`_COMPRESSED` in the prose, `.COMPRESSED` in the example),
  and missing examples. Pick one spelling and use it everywhere. Never patch
  the copied table: rebuild every example from the canonical.
- **Every level gets an example**, even when the brief has none. It exercises
  each stated rule once, including ties and boundaries.

## Writing the canonical

`solution/solution.py` is the worked answer the next author reads, so it is
written to be read. Whatever the class keeps — an account, a session, one
version of a recipe — is a `@dataclass`, never a naked class, a tuple or a set
of parallel dicts: the fields get names and types, and the rules that belong to
the record (`alive_at`, `overlap`, `rank`) live on it instead of in the manager.
Use `slots=True`, and `frozen=True` where a change means a new value rather
than a mutation. The `solution/level<N>.py` checkpoints follow the same style,
so the difference between two of them is the work the level adds and nothing
else.

## Test modules

Tests are authored Python, not data. Each case is a function taking the
solver's class:

```python
from icf_testkit import case, expect

@case("a field is gone at exactly ts + ttl")
def ttl_boundary(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "v", 9)
    expect(db.get(10, "k", "f"), None, "the window is [1, 10)")
```

* `@case("…")` — the label is what a *visible* case shows in the UI, so write
  the behaviour being checked, not a test name.
* The kit gives you `expect`, `expect_true`, `expect_close` and
  `expect_raises`. A bare `assert` also works, it is just less informative.
* Each case gets its own timer and its own captured stdout. Build fresh
  instances inside the case; nothing is shared between cases.
* Helper functions in the module are fine — only `@case` functions are
  collected.
* `icf_testkit` only exists inside the sandbox, so these modules are not
  importable (and not type-checked) outside it. That is deliberate.

### What makes a good suite

Write the **boundary cases from the specification first** — the moment a TTL
expires, an empty scan, a rollback whose name is now taken — and only then add
randomised sequences compared against a small reference model written *inside*
the test module. Model-based cases catch what enumeration misses; the hand-
written ones are what stop a wrong canonical from being enshrined.

Visible cases teach, hidden cases grade. Put the ones that explain the rule in
`visible.py` and the mean ones in `hidden.py`.

## The gate

```bash
python icf/scripts/verify_icf.py --slug <slug> -v
```

1. **Spec** — four levels, statements present, the starter declares every
   advertised method, the slug is usable.
2. **The starter fails** — if a stubbed method passes a case, that case is
   vacuous (`None` is a real answer for a lot of methods). Sharpen it: assert a
   positive fact in the same case.
3. **The canonical passes** every case of every level.
4. **Each level earns its place** — level N's tests must *fail* against
   `solution/level<N-1>.py`. Write those checkpoints; they are the only
   machine check that a level asks for something new.

`make icf-verify` runs it over the whole set, and `make check` includes it.
