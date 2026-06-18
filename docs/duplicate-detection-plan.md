# Duplicate-problem detection — design plan

> **Status: proposed (not started).** A plan for preventing duplicate problems
> from entering the bank, where "duplicate" includes semantic rephrasings and
> trivially reduction-equivalent problems — not just identical text. Captured for
> later; revisit before implementing. See also `docs/roadmap.md`.

## Motivation

"Duplicate" here is broader than identical text:

- A **rephrasing** of an existing problem (same task, different words).
- A **trivial reframing / reduction**: e.g. *"number of ways to climb `n`
  stairs taking 1 or 2 steps"* vs *"number of ways to write `n` as an ordered
  sum of 1s and 2s."* These look unrelated but reduce to each other (both are
  Fibonacci). `climbing-stairs` is already in the bank, so this exact case is a
  real latent duplicate and a good test target.

## Where this hooks into the repo

All add-paths converge on two choke points:

- `store.upsert_problem` (DB) + `content.write_problem_files` (disk mirror),
  reached via the admin UI (`admin.new_submit` / `generate_submit`), the AI
  generator (`generator.generate_problem`), and the file→DB seed
  (`seed_from_content`).
- The skills (`/add-problem`, `/new-problem-set`) and the `problem-author`
  subagent write files that then flow through seed.

There are already two pre-publish gate scripts — `scripts/seed.py` (canonical
solution passes its tests) and `scripts/audit.py` (statement↔judge consistency).
A dedup gate belongs right next to them.

The bank is small (~30 problems) and grows slowly, so we can afford expensive
per-add checks against the whole bank.

## 1. Three kinds of "duplicate," each needs a different signal

| Kind | Example | What catches it |
|------|---------|-----------------|
| **Textual** (copy/paste, light rephrase) | Two Sum reworded | Lexical fingerprint (cheap) |
| **Structural** (same I/O shape & technique) | two different 1-D DP counting problems | Structural + behavioral fingerprint |
| **Reduction-equivalent** (the hard one) | climbing stairs ↔ compositions of {1,2} summing to n | LLM reduction judge (+ behavioral fingerprint when both reduce to the same sequence) |

No single test covers all three. The design is a **funnel**: cheap filters
shrink the candidate set; an expensive LLM reasoning step makes the final call
on only a handful of neighbors.

## 2. The detection funnel (cheapest → most expensive)

**Stage 0 — Normalize into a "problem descriptor."**
Per problem, derive a compact, wording-independent descriptor (cached). Fields:

- `core_task` — one normalized sentence ("count length-n sequences over {1,2}
  summing to n").
- `input_essence` / `output_essence` — abstract types (scalar `n`, int array,
  graph; count / boolean / optimal value / list).
- `technique` — 1-D DP, two-pointer, hashmap, BFS, binary search…
- **`recurrence_or_closed_form`** — e.g. `f(n)=f(n-1)+f(n-2)`, "Fibonacci,"
  "Catalan." *This field unifies stairs and compositions — both normalize to the
  Fibonacci recurrence.*

Produced once by Claude (already wired to the Anthropic API) and stored in a
dedup index.

**Stage 1 — Lexical fingerprint.** MinHash/SimHash over the normalized
statement. Catches textual dupes instantly across the whole bank. Misses
reductions.

**Stage 2 — Behavioral fingerprint (the cheap silver bullet for reductions).**
For the common "scalar in → scalar/int out" family, run the **canonical
solution** over a fixed battery of normalized inputs (n = 0..K) and hash the
resulting **integer sequence**. Two problems that reduce to each other produce
the *same sequence* regardless of wording — climbing-stairs and
compositions-of-{1,2} both emit `1,1,2,3,5,8,…`. Identical (or shifted) sequence
⇒ near-certain duplicate, at zero LLM cost. Generalize later to other normalized
input shapes; where I/O shapes don't line up, this stage abstains.

**Stage 3 — Semantic retrieval.** Embed the Stage-0 descriptor; take top-K
nearest neighbors as candidates. Anthropic has no embeddings endpoint — use a
local sentence-transformer, **or**, given the bank's size, skip embeddings and
just union the Stage-1/2 candidates. Add embeddings only when the bank gets large.

**Stage 4 — LLM reduction judge.** For each shortlisted pair, ask Claude:
*"Do these reduce to one another or share the same core algorithm? Return
`{distinct | variant | duplicate}`, a one-paragraph reduction sketch, and a
confidence."* The **only** layer that reliably catches non-obvious reductions.
Cache the verdict keyed by the pair's content hashes so it never re-runs unchanged.

## 3. Decision policy (assist, don't silently block)

- **duplicate** (high confidence, or identical behavioral fingerprint) → block
  the add; show the matched slug + reduction sketch.
- **variant** (same core, deliberately harder/constrained twist) → warn; require
  an explicit `intentional_variant_of: <slug>` tag to proceed.
- **distinct** → pass.
- Every block is **human-overridable**; overrides recorded in an **allowlist**
  (slug-pair) so the same intentional near-duplicate never re-nags.

Reduction-equivalence is undecidable in general, and the judge has both false
positives ("same DP shape, different meaning") and false negatives (clever
reductions). The system must inform a human, never be the sole authority.

## 4. Prevention is cheaper than detection (close the loop in the generator)

Before any detection, feed the existing bank's titles + Stage-0 descriptors into
the generator's prompt as a "do not duplicate / pick a genuinely different core"
list. The guidelines already nudge "prefer fresh framings"; make it concrete and
data-driven. On a post-generation duplicate verdict, auto-retry once with the
offending neighbor added to an explicit avoid-list before surfacing to the admin.

## 5. Where it lives in the repo

- **`app/dedup.py`** — reusable library: descriptor extraction, the three
  fingerprints, candidate retrieval, the LLM judge, the decision policy.
- **Dedup index sidecar** — `content/.dedup-index.json` (or a small DB table)
  holding `{descriptor, lexical_sig, behavioral_fp, embedding}` per slug, keyed
  by content hash. Built/refreshed by **`scripts/build_bank.py`**; invalidated
  when a problem's content changes.
- **`scripts/dedup.py`** — two modes: (a) check one candidate against the bank
  (pre-publish gate alongside `seed.py`/`audit.py`); (b) audit the **whole bank
  pairwise** for latent internal dupes — run once now; should flag
  climbing-stairs-style overlaps.
- **Generator + admin** — call the library before `_save`; render warnings in the
  admin add/generate UI.
- **Skills & subagent** — add a "check against existing bank" step to
  `/add-problem`, `/new-problem-set`, and `problem-author`, referencing a new
  short section in `specs/problem-authoring-guidelines.md` so the rule lands on
  every authoring path at once (manual + AI).

## 6. Validate the detector itself

Reduction detection quietly fails to work unless measured. Build a tiny labeled
set: known equivalences (stairs↔compositions, plus synthetic rephrasings of
existing problems) as positives, and clearly-distinct pairs as negatives. Track
precision/recall to tune the LLM-judge confidence threshold and the
behavioral-fingerprint sensitivity. The existing ~30-problem bank is the initial
corpus.

## 7. Suggested phasing

1. **Phase 1 (cheap, high value):** Stage-0 descriptors + Stage-1 lexical +
   Stage-2 behavioral fingerprint + `scripts/dedup.py` whole-bank audit. No LLM
   needed for the fingerprint path; immediately catches the stairs case and all
   textual dupes.
2. **Phase 2:** Stage-4 LLM reduction judge on shortlists + decision policy +
   allowlist; wire into generator and admin UI.
3. **Phase 3:** prevention loop in the generator + spec/guideline updates +
   skill/subagent steps.
4. **Phase 4 (only if the bank grows large):** embeddings + ANN retrieval to
   keep the shortlist cheap.

## Key bet

**Stage 2.** Many LeetCode-style counting/DP problems collapse to the same
integer sequence, so an OEIS-style behavioral fingerprint catches a surprising
share of reduction-duplicates for nearly free — leaving the LLM judge to handle
only the cases where I/O shapes genuinely differ.
