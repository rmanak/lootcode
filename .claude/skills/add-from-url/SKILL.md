---
name: add-from-url
description: Given a problem URL (LeetCode or any other site), check whether the lootcode bank already has that problem under any slug or title. If it doesn't, author the problem, verify it, and import it into content/problems-extended/. Use when the owner pastes a problem link and asks "do we have this?", "add this", or just drops the URL.
argument-hint: <problem-url> [more-urls...]
---

Do we have the problem at **$ARGUMENTS** in our question bank? If not, add it
to `content/problems-extended/`.

Several URLs means the same procedure for each one, followed by a single report.
The owner wants this to run without interruptions, so don't ask questions. Stop
early only where this file says to, and report why.

`$S` below means `<session scratchpad>/url-import`. Run every command with
`.venv/bin/python`.

## 1. Look it up

```
.venv/bin/python scripts/find_problem.py "<url>" --save $S/src
```

The script fetches LeetCode problems through LeetCode's GraphQL endpoint.
Premium statements come from the doocs/leetcode mirror. It checks the problem
against **both** content roots and prints a verdict and a ranked candidate
table. With `--save` it also writes `$S/src/<slug>.json`, which holds the
statement as draft Markdown, the figure URLs, LeetCode's tags (raw and
canonical), the difficulty, the signature (`meta`) and the example inputs.

- **IN BANK** (exit 0) means a slug or title match. Report the slug, root,
  title, difficulty and `http://127.0.0.1:8000/problems/<slug>`, then **stop**.
  If an `also …` line appears, the bank already holds a twin. Mention it, but
  leave it alone: deduplicating (`scripts/remove_problem.py <old>=<new>`) is
  the owner's decision.
- **LIKELY IN BANK** (exit 3) means a bank problem grades the same example
  inputs. Read its `problem.md` and signature next to the fetched statement. If
  it is the same task (same input gives the same output, even renamed or
  reframed, for example "return the array" instead of "modify in place"), treat
  the problem as IN BANK and stop. If it is a sibling ("… II", a different
  constraint or a different output), continue as NOT FOUND.
- **NOT FOUND** (exit 1): before adding, still read any candidate showing
  `fname`, `example`, or `stmt ≥ 0.5`. Many of the ~1.2k bank problems were
  imported under renamed slugs (`kth-largest-element`, `path-sum-exists`,
  `meeting-rooms-required`…), and a rename with a reworded title only shows up
  through these signals.

**URLs from other sites:** the script does not fetch them. Use WebFetch on the
page. If the page names or links the LeetCode original, rerun the script with
the LeetCode URL, which gives you tags, difficulty, signature and examples.
Otherwise, save the statement to `$S/src/<slug>.md` and rerun with
`--title "<title>" --statement $S/src/<slug>.md`.

**Statement unavailable** (both LeetCode and the mirror failed): use WebSearch
for `"<id>. <title>" leetcode` and take the full statement from another
mirror. Give up only if no source has it.

**Stop without adding, and say why**, when the harness can't judge the problem:

- a non-`Algorithms` category (Database, Shell, Concurrency, JavaScript, pandas)
- interactive problems
- non-deterministic output (`getRandom`, `shuffle`)
- compositional round-trips (`serialize` ↔ `deserialize`); see
  `docs/design-problems.md`
- many valid answers that no `compare` mode (`exact` / `unordered` /
  `set_of_lists`) can grade

Offer to re-author it as a judgeable Python problem, but don't do it unasked.

## 2. Author it in staging

Use LeetCode's `titleSlug` as the slug. Stage the problem at
`$S/staging/<slug>/` in the importer's layout (`docs/importing-problems.md`).
Read and follow the specs, as for any authoring:
`specs/problem-authoring-guidelines.md` and `specs/problem-schema.md`.

**`meta.json`** is `{"title": …, "body": …}`. The body is the statement Markdown
**without** the `# Title` line, which the importer adds. Start from
`statement_md` in the saved JSON, then clean it up:

- Use the bank's `10^4` / `2^31 - 1` style. The converter turns `<sup>` into
  `^`. A statement from another site may have collapsed exponents (`105` →
  `10^5`), so check that each value is plausible.
- `<sub>` came out as `x_i`. That reads fine inside code spans; reword it
  elsewhere.
- Drop LeetCode cruft such as "Note: This question is the same as …" links.
  Keep a Follow-up only if it's informative, because it is never graded.
- **Reframe for the harness.** It calls one top-level function (or replays one
  class) and compares the **return value**:
  - For a `void` / in-place signature (`meta.output.paramindex`), return the
    modified value instead, and update the statement sentence and the examples
    to match.
  - Trees and linked lists use the rich types (`TreeNode`, `ListNode`,
    `DoublyLinkedList`).
  - Other node classes (graph `Node`, `NestedInteger`, random pointers) need a
    plain-JSON encoding. First find a comparable bank problem (`clone-graph`,
    `flatten-nested-list-iterator`, …) and copy its framing.
- **Figures.** Download each raster URL in `images` (jpg/jpeg/png/gif/webp)
  with `curl -sfL -o $S/staging/<slug>/assets/<name>`. Reference each one as
  `![Example N: <what it shows>](assets/<name>)`; the importer rewrites the
  path. Redraw an SVG figure, or one whose download fails, as a hand-written
  SVG following `docs/problem-images.md`. If the source has no figure, apply
  that doc's rubric and don't add one by default.

**`generated_full_problem.json`**: you write it yourself, and
`app/llm/problem_prompt.txt` is the contract. Read it first and follow it
exactly, as the `problem-from-statement` agent does. Choices that are specific
to this flow:

- `difficulty` is LeetCode's. `tags` is `tags_canonical` from the saved JSON
  **as-is**: LeetCode's topic tags put through `app.tags.normalize_tags`, which
  is the bank's tag ground truth. Use the `canonical-tags` skill only if that
  list is empty (non-LeetCode source).
- Take names from `meta`: function or class name, parameter names, methods.
  Map the types onto the prompt's TYPES vocabulary (`integer` → `int`,
  `integer[]` → `int[]`, `double` → `float`, `boolean` → `bool`, `character` →
  `string`, so `character[][]` → `string[][]`; `list<integer>` → `int[]`,
  `list<list<string>>` → `string[][]`).
- Set `compare` to match what the statement promises about answer order.
- The canonical uses the standard library only and the **intended** complexity.
  Quadratic canonicals have been a recurring defect here.
- **Tests:**
  - Every statement example is a visible case, and its stated output must equal
    what the canonical returns. A mismatch means the canonical or your reframing
    is wrong.
  - Then add hidden cases: minimum sizes, extreme values, empty input where
    allowed, ties, duplicates and negatives, plus at least one input near the
    constraint limits so that a brute force times out.
  - Write the input validator first, as `$S/validators/<slug>.py`, following
    the `docs/input-validators.md` contract. Model it on
    `content/problems-extended/number-of-islands-ii/input_validator/input_validator.py`.
    The validator checks every constraint line and treats `bool` as not `int`.
    For a class problem, start from what `scripts/generate_class_validators.py`
    would emit and add the value bounds.
  - Generate hidden inputs with a scratch script. Keep only the inputs that
    `validate_input` accepts, and take `expected` from the canonical's output,
    never from your own hand calculation.
  - Cross-check the canonical against a brute force on many small random
    inputs.
  - Keep sampling until the **outputs** are varied.
  - Mind the traps in CLAUDE.md's "Strengthening a weak suite":
    - Float answers must be bit-stable.
    - Promises in the statement ("exactly one solution", "guaranteed
      reachable") must hold on every generated input. `validate_input` does
      not check these.
  - Keep a whole run's results under about 1 MB.
- Hints: up to 3, progressive. The last one hints at the insight and does not
  transcribe the solution. The tier rules are in `specs/problem-schema.md`.

Verify in staging before importing:

```
.venv/bin/python scripts/test_llm_output.py --strict $S/staging/<slug>/generated_full_problem.json
.venv/bin/python scripts/verify_json.py $S/staging/<slug>
```

## 3. Import

```
.venv/bin/python scripts/import_generated_problems.py $S/staging --slug <slug> --dry-run
.venv/bin/python scripts/import_generated_problems.py $S/staging --slug <slug> -y
```

The default target is `content/problems-extended/`, which is the one you want.
Never pass `--out content/problems`. Never `--overwrite` a problem you didn't
just add. If a gate fails, fix the staged problem and rerun; don't route around
the gate.

The importer doesn't copy validators. Install yours at
`content/problems-extended/<slug>/input_validator/input_validator.py`.

## 4. Verify and report

```
.venv/bin/python scripts/verify_bank.py <slug>
.venv/bin/python scripts/check_constraint_validators.py --slug <slug>
.venv/bin/python scripts/check_db.py
```

If a dev server is up (`curl -s -o /dev/null -w '%{http_code}'
http://127.0.0.1:8000/problems/<slug>`), confirm that the page and each figure
URL return 200. If the local Qwen server on `:8080` is up, also run
`scripts/improve_hints.py audit --slug <slug>` and fix any hint it flags.

Report briefly:

- the verdict, slug, root, difficulty and tags
- test counts (visible/hidden) and figures
- any reframing you did
- each gate's status
- the link

There is nothing to commit, because `content/problems-extended/` is gitignored.
Don't add the problem to any collection unless asked.
