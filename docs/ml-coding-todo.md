# ML coding: what's left (resume here)

**Last updated 2026-10-31.** To pick this up in a new session, say
**"resume docs/ml-coding-todo.md"**, or name one item, e.g. "do item 1b". Items are
in the recommended order. Tick them off here as they land, so this file stays the
single source of what's left.

Background: [`ml-coding-plan.md`](ml-coding-plan.md) (why, and the decisions) ·
[`ml-coding-problem-bank.md`](ml-coding-problem-bank.md) (62 candidate problems) ·
the "Machine-learning problems" section of `specs/problem-authoring-guidelines.md`
(the authoring rules).

## Where things stand

**Done and verified** (`make check` green; real server against the real DB; the
`executor-security-reviewer` approved, and its findings for this change are fixed):

- numpy importable in the sandbox. `sandbox.SINGLE_THREAD_ENV` is load-bearing:
  without it, `import numpy` dies under `RLIMIT_AS`.
- `compare: "close"`: floats within rel `1e-6` / abs `1e-9`, ints exact,
  overflow-safe. Returned numpy values are converted by `harness._plain`.
- The `machine-learning` tag (45 tags) and the `ml-coding` collection.
- Problems: `pairwise-ranker-i-loss-and-gradient`, `pairwise-ranker-ii-training`,
  `softmax-cross-entropy-loss-and-gradient` (item 1a), `k-means-from-given-centroids` (item 1b),
  `kv-cache-attention` (item 1c), `roc-auc` (item 1d). **The pilot is complete.**
- **Phase 3, Waves A (13), B (9), C (8), D (10), E (12), F (9) and G (2),
  done 2026-10-31.** The collection now has 69 problems. See item 2. The
  planned list is finished. What remains is optional (see "Beyond the
  plan" under Wave G).
- **Harness fix, 2026-10-31:** class-problem outputs are copied when each call
  returns (`harness._snapshot`); see item 2, Wave A notes. The
  `executor-security-reviewer` result is recorded there.

**Committed 2026-11-01** (see item 5).

---

## 1. Finish the pilot ✅ done 2026-10-31 (1a–1d)

They were chosen so the set exercises every pattern from the plan. Do them one at
a time with the recipe below, and **vet every case** (the step that caught the
ill-conditioned case in Ranker II).

### The recipe (same for each problem)

1. Create `content/problems/<slug>/{problem.md, meta.json, tests/, starters/python/, solution/, input_validator/}`.
   Copy the shape of `content/problems/pairwise-ranker-i-loss-and-gradient/`:
   - **Statement:** Unicode math in a code block; say "numpy and the Python
     standard library"; state the tolerance sentence; `## Constraints`; 2–3
     `## Examples`. **Never write "you may return"**: `scripts/audit.py` reads it
     as any-order language.
   - **meta.json:** `compare: "close"`, a camelCase function name,
     `tags: ["machine-learning"]` (plus a technique tag only if it is genuinely the
     point, e.g. `design` for a class problem), and 3 hints (≤ ~25 words; tier 3 is
     the insight, never the formula).
   - **Validator:** hand-written, with a docstring saying so. It enforces every
     stated bound **and every promise the statement makes about the answer**
     (e.g. "at least one positive and one negative").
2. Build `tests/cases.json` (≈10–11 cases: 2–3 visible, the rest hidden) with a
   copy of `scratchpad/ml-coding/gen_softmax_ce_cases.py` (git-ignored, local; the
   cleaner template, one problem per script) or `gen_ranker_cases.py` (an
   iterative problem's perturbation check).
   - The canonical is the only oracle.
   - Each case must pass `validate_input`.
   - ≥ 2 independently written correct implementations (pure-Python loop +
     reordered numpy) must agree with the canonical to 1e-9.
   - Iterative problems also get a 1e-12 perturbation check.
   - Every known-wrong variant must fail at least one **visible** example.
   - Where the statement mentions stability, the naive formula must fail a hidden
     case.
3. Add the slug to `content/collections/ml-coding.json`.
4. Gates:
   - `scripts/verify_bank.py <slug> -v`
   - `scripts/check_constraint_validators.py --slug <slug>`
   - `scripts/audit.py -q`
   - `scripts/check_db.py`, then `scripts/seed.py -j 8`, then `make check`
5. Real server (CLAUDE.md, "done means the real thing ran"):
   - Start `uvicorn` on :8000, but only if nothing else is on it.
   - Open `/problems/<slug>` and `/?collection=ml-coding`.
   - POST `/api/problems/<slug>/run` twice: once with the canonical, once with a
     numpy-returning variant.
   - Stop the server with a pattern that can't match its own shell, e.g.
     `pkill -f "[u]vicorn app.main"`.
   - Run `check_db.py` again.
6. Mark the row shipped in `ml-coding-problem-bank.md`, tick it here, and update
   the memory note.

### 1a. Stable softmax + cross-entropy (bank #23): F + stability ✅ shipped 2026-10-31

`softmax-cross-entropy-loss-and-gradient`, medium, 11 cases (3 visible). All gates
green, `make check` green, and the real server graded the canonical and a
numpy-returning variant 11/11 and the naive formula 6/11. Vetted against 12 wrong
variants. The 9 ordinary ones (incl. softmax down the wrong axis, log₂, a forgotten
one-hot, and `log(p + eps)` for eps 1e-7/1e-12/1e-15) each fail a visible
example. The 3 stability ones fail hidden cases only:

- no max subtraction
- stable softmax, then `log(p)`: underflows to `log(0)`
- logits clipped to ±500

Hints still need item 2's audit.

### 1b. k-means from given initial centroids (bank #10): RI + PL + TB ✅ shipped 2026-10-31

`k-means-from-given-centroids`, medium, 14 cases (3 visible), all gates and
`make check` green. On the real server the canonical and a raw-ndarray/int64
variant scored 14/14, and the empty→`nan` bug scored 9/14 (a clean wrong
answer, no crash on the NaN). Generator: `scratchpad/ml-coding/gen_kmeans_cases.py`.

- The near-tie vetting is an **exact `Fraction` re-run**. An exact tie is allowed
  only when every tied value is a small dyadic rational, because only then do all
  float formulas (direct, `|p|²−2p·c+|c|²`, sqrt) see the same tie.
- Five correct implementations agree, including "never stop early" and "stop
  when no centroid moved", since a converged state is a fixed point.
- 10 wrong variants each fail a visible example: the five planned below, plus
  empty→`nan`/origin, labels recomputed from the final centroids, one iteration
  too many, and online (MacQueen) updates.
- The statement pins `labels` as the **last assignment**. Don't re-assign after
  the final update; example 2 shows why.

Original spec:

- `kMeans(points, initialCentroids, maxIters)` → `[centroids, labels]`.
- Labels are ints, so `close` compares them exactly.
- **Pin all of these in the statement:**
  - Lloyd's algorithm.
  - One iteration = assign every point, then update every centroid.
  - Squared Euclidean distance.
  - A distance **tie goes to the lowest centroid index**.
  - An update is the mean of the assigned points.
  - An **empty cluster keeps its previous centroid**.
  - Stop when no assignment changes, or after `maxIters` iterations.
  - Return the centroids in their initial order.
- Use integer coordinates to make **exact** ties deliberately: they are fair
  because the tie rule is pinned. Vet away **near**-ties: in every iteration of
  the canonical, the best and second-best distances must differ by more than
  1e-9 relative, unless exactly equal.
- **Wrong variants:**
  - tie → highest index
  - empty cluster re-seeded
  - Manhattan distance
  - centroids returned sorted
  - one iteration too few

### 1c. KV cache (bank #40): class kind ✅ shipped 2026-10-31

`kv-cache-attention`, medium, tags `machine-learning` + `design`, 13 cases
(3 visible). All gates and `make check` green. On the real server the canonical
and an ndarray/`np.int64`-returning variant scored 13/13, and the overflowing
softmax scored 10/13. Generator: `scratchpad/ml-coding/gen_kvcache_cases.py`.

- **Deviation from the spec below:** the constructor is
  `KVCache(dim, maxLen)`. A **sliding window** evicts the oldest entry once
  `maxLen` entries are held. Without it the class is just two lists; with it,
  eviction order and `size()` are real state to get wrong (and it's how
  sliding-window attention bounds memory).
- 9 wrong classes each fail a visible example: no 1/√dim, 1/dim, no eviction,
  evict newest, a ring buffer that always overwrites slot 0 (example 2 evicts
  twice to catch it), window ±1, uncapped `size`, and keys/values swapped.
  No max subtraction fails 3 hidden cases only.
- Found while doing it: a fenced block **inside a list item** renders as inline
  code. Now in the ML authoring rules.

Original spec:

- `class KVCache` with:
  - `__init__(self, dim)`
  - `append(self, k, v)` → `void`
  - `attend(self, q)` → the vector `softmax(q·Kᵀ/√dim)·V` over everything
    appended so far
  - optionally `size()`
- Tags: `machine-learning`, `design`. Tests are operation sequences
  (`specs/problem-schema.md`, "Class-based problems").
- **Validator:**
  - Start from `scripts/generate_class_validators.py`'s structural output.
  - Hand-tighten the value bounds.
  - **Enforce "`attend` is only called on a non-empty cache"**, or pin what
    an empty attend returns.
- Stability: large `q·k` must not overflow, so the softmax needs the max trick.
- The vetting alternates must be classes too, replayed over the same sequences.

### 1d. ROC-AUC (bank #16): F + TB ✅ shipped 2026-10-31

`roc-auc`, medium, 12 cases (3 visible), all gates and `make check` green.
Generator: `scratchpad/ml-coding/gen_rocauc_cases.py`.

- **Size decision:** `N ≤ 5·10⁴`, both large cases balanced (P·Q ≈ 6.25·10⁸).
- **And `timeLimitMs: 2000`**, the first problem below the 10 s default.
  CPython 3.12 runs the plain double loop at about 15 ns per pair, so at 10 s
  the brute force passed one large case and failed the other on noise.
- Real server, at 2 s:

  | Submission | Result |
  |---|---|
  | canonical, pure-Python O(N log N) sweep (~0.02 s) | 12/12 |
  | pure-Python pairwise | 10/12, per-test timeouts; the run is not killed |
  | full-broadcast numpy | 10/12, per-test errors |
  | row-chunked numpy pairwise | 12/12, accepted as planned |
- 7 wrong variants each fail a visible example: ties as 0, ties as 1, labels
  inverted, 11 fixed thresholds, ROC steps that ignore ties, ordinal ranks, and
  dividing by C(N,2). Example 2 lists the positive first in **both** tie groups;
  with mixed orders, the two tie-order bugs' errors cancel.

Original spec:

- `rocAuc(scores, labels)` → float.
- **Definition:** the probability that a random positive scores above a random
  negative, with **ties counting ½**.
- The validator must enforce **at least one positive and one negative**.
- **Decide the size.** The intended solution is the O(N log N) rank-sum;
  O(N²) pairwise is the brute force. To make the brute force fail you need
  N ≈ 5·10⁴.
- Mind `docs/code-execution.md`: a long numpy broadcast can't be interrupted
  per test.
  - The full N² `bool` array would hit `MemoryError` under `RLIMIT_AS`,
    which is fine: it fails as a per-test error.
  - A chunked version would just run long, and then the whole run is killed.
  - Probably keep N ≤ ~5·10⁴ and accept that a well-chunked numpy pairwise
    may pass.
- **Wrong variants:**
  - ties counted as 0 or 1
  - AUC from a few fixed thresholds
  - labels inverted

## 2. Phase 3: the rest of the bank (ACTIVE, started 2026-10-31)

The owner said on 2026-10-31: keep creating problems from the whole bank, and
**no hints for ML problems**. New problems ship with no `hints` key, which is
valid: absent means "no hints". The six pilot problems keep the hints they have.

**Recipe:** the same as item 1 above, minus the hints. Two shortcuts:

- **Generators use `scratchpad/ml-coding/mlgen.py`** (git-ignored), a shared
  vetting harness. A generator holds only the cases, the alternates and the
  wrong variants, then calls `vet()`. `vet()` grades with the judge's own
  `_close`, and also checks the validator, finite output, the 1 MB result
  budget, visible failures for wrong variants and hidden failures for
  stability variants. File names: `gen_<short>.py`; `--write` writes
  `cases.json`.
- **Gates run per problem**: `verify_bank.py <slug> -v` and
  `check_constraint_validators.py --slug`. **Per wave**: `seed.py`, `audit.py`,
  `make check`, then a real-server pass (canonical + one numpy-returning
  variant per problem, through the owner's uvicorn on :8000 if it is up).

Tick each box when its problem has passed the per-problem gates. Write `(wave
gates ✅)` after a wave once the per-wave gates are green too. A problem is
marked **Shipped** in `ml-coding-problem-bank.md` only after the wave gates.

### Wave A: the core interview set (wave gates ✅ 2026-10-31)

All 13 problems passed the per-problem gates, then the wave gates:

- `seed`, then `audit` (ALL CONSISTENT, 1201 problems)
- `make check` (576 tests; 17106/17106 bank cases); `check_db` OK before and
  after
- Real server (the owner's uvicorn on :8000): each canonical and a
  numpy-returning variant scored full marks, all 13 pages returned 200, and
  `/?collection=ml-coding` lists 19 problems

Generators: `scratchpad/ml-coding/gen_{logreg,attention,mha,layernorm,nms,knn,beam,bpe,sampling,mlp,adam,pca,tree}.py`.

Notes and deviations from the one-line specs:

- **Harness bug found and fixed (A11).** `_run_class` used to serialize the
  outputs list only after the whole call sequence. A method that returned its
  internal list or numpy array and then mutated it in place had every earlier
  output overwritten by the final state. That broke the natural Adam
  (`self.p -= …; return self.p`), and any class problem that returns an
  internal list. Now each result is copied as JSON when its call returns
  (`harness._snapshot`), with a per-call error that names the method.
  - Tests: `tests/test_executor.py::test_class_outputs_are_recorded_when_each_call_returns`
    and `…_not_json_names_the_method`.
  - `make check` is still green, so no existing class problem relied on the old
    behaviour. On the real server, the in-place Adam now scores 11/11.
  - `docs/design-problems.md` is updated.
  - **`executor-security-reviewer` verdict: sound, not blocking.** The change
    is stricter than before: a hostile `__iter__`/`tolist()` now times out
    that one test instead of killing the whole run. It filed five Low or Info
    findings, all failing closed. Two touched the new code and are fixed: the
    error branch now disarms the timer first, and there is a new test,
    `test_a_class_return_that_hangs_while_encoding_times_out_alone`. The doc
    drift in `docs/code-execution.md` is also fixed. The other three predate
    this work: F3 and F7 (below) already covered two, and the third is the new
    F11.
- **Integer answers use `compare: "exact"`** (A5 NMS, A6 kNN, A8 BPE), since
  there is no float to tolerate. That's honest: `close` would grade them the
  same way.
- **A9 returns `[token, finalProbs]`**, not just the token, so renormalization
  bugs show up. Exact-boundary cases (a running total landing exactly on
  `topP` or `u`) were **dropped**: a log-space solution rounds differently and
  would flip. The statement still states the rule (`>= topP`, `> u`), and every
  test keeps a 1e-9 margin from both.
- **A13 tie rule:** gains within `1e-9` count as tied (equal fractions round
  differently in different formulas). Vetting uses exact `Fraction` gains: any
  gain not tied with the best trails it by more than 1e-6.
- **A12 validator uses numpy** (an eigendecomposition) to enforce the promises
  that make the answer unique. Validators only run in offline tooling, and
  numpy is a runtime requirement.
- **Equivalent "bugs" dropped from the wrong-variant lists:**
  - beam search where finished hypotheses free their beam slot
  - beam search where EOS beams stay in the beam unextended
  - sampling with the temperature applied after the softmax (`p^(1/T)`, renormalized)

  With log-probs `≤ 0` and a raw-sum score, each of these returns the same
  answer as the pinned rule, so they are not wrong.

- [x] A1 `#4` `logistic-regression-gradient-descent`: PL. `w, b` start at 0;
  full-batch GD with `lr` and `steps` as inputs; mean BCE. Return
  `[w, b, lossHistory]`, with the loss taken before each step. A stable BCE
  at large margins.
- [x] A2 `#37` `scaled-dot-product-attention`: F. `Q, K, V, mask`
  (1 = may attend). The validator enforces at least one allowed key per
  query. Stability with large scores.
- [x] A3 `#38` `multi-head-causal-self-attention`: F. `X, Wq, Wk, Wv, Wo,
  numHeads`; heads split along contiguous column blocks; causal mask.
- [x] A4 `#27` `layer-norm-forward-and-backward`: LG. `x, gamma, beta, dy,
  eps` → `[y, dx, dgamma, dbeta]`, with biased variance.
- [x] A5 `#54` `non-maximum-suppression`: F+TB. Boxes `[x1,y1,x2,y2]`;
  suppress when IoU `>` the threshold (strict); score ties go to the lower
  index. Return the kept indices.
- [x] A6 `#9` `k-nearest-neighbors-classifier`: F+TB. Squared Euclidean
  distance; distance ties go to the lower training index; vote ties go to
  the smallest label.
- [x] A7 `#43` `beam-search-decoding`: F+TB. A bigram log-prob table is the
  "model"; beam width, max length and an EOS token; pin the score ties and
  the finished-beam handling.
- [x] A8 `#44` `bpe-tokenizer`: F+TB. Learn `numMerges` merges from a corpus
  (pair-count ties go to the lexicographically smallest pair), then encode a
  word. Pure strings, no numpy needed.
- [x] A9 `#42` `top-k-top-p-sampling`: RI. Logits, temperature, `k`, `p` and a
  uniform `u` → a token id. Pin the order and the cumulative-mass boundary.
- [x] A10 `#26` `two-layer-mlp-backprop`: LG. `X, y, W1, b1, W2, b2` with
  ReLU and softmax CE → loss plus all four gradients. Pin `relu'(0) = 0`.
- [x] A11 `#30` `adam-optimizer`: CL. `Adam(params, lr, beta1, beta2, eps)`
  with `step(grad)` → params; bias correction pinned.
- [x] A12 `#12` `principal-component-analysis`: F+TB. Center the data,
  covariance with `N-1`; the top-`k` components with a pinned sign; return
  the components and the projections. The validator ensures well-separated
  eigenvalues.
- [x] A13 `#11` `decision-tree-best-split`: F+TB. The Gini gain of every
  midpoint threshold; ties go to the lowest feature, then the lowest
  threshold.

### Wave B: classical ML (wave gates ✅ 2026-10-31)

Wave gates:

- `seed` and `audit` ALL CONSISTENT (1210 problems)
- `make check` green (577 tests; 17207/17207 bank cases); `check_db` OK
- Real server: every canonical and a numpy-returning variant scored full
  marks. Two deliberately wrong submissions scored 2/11 (elastic net with
  `sign(0) = +1`) and 10/12 (Pegasos with `<= 1`).
- All 9 pages returned 200. The collection says "28 problems" (it pages at 25).

Generators: `scratchpad/ml-coding/gen_{linreg,ridge,softreg,enet,pegasos,perceptron,nb,mf,adaboost}.py`.

Notes:

- **B2 is ridge rather than plain OLS.** `lam = 0` is the normal equation, so
  one problem covers both.
- **B4 keeps the subgradient** (the interview version) rather than proximal
  ISTA. The discontinuity at 0 is vetted two ways:
  - a 1e-12 perturbation check
  - a replay that flags any weight `sign` reads within 1e-9 of zero (unless
    it is exactly 0)

  The statement says the history need not decrease.
- **B5 and B9 ties** are vetted with exact Fractions. Pegasos allows a margin
  of exactly 1 only at steps `t <= 3` with a power-of-two `lam` and integer
  features, where float formulas are exact too. One visible and one hidden
  case test it; the final `w` only depends on which steps violated, so the
  first search found a tie order that `<=` also passed.
- **B9's polarity order** only matters when every stump has error 0.5.
  A hidden "coin flip" case checks it (alpha 0, weights unchanged).
- **B6 uses integers** and `compare: "exact"`.

- [x] B1 `#2` `linear-regression-gradient-descent`: PL, with MSE history.
- [x] B2 `#3` shipped as `ridge-regression-closed-form`: F. One problem
  covers both: `lam = 0` is the normal equation, and the tests include OLS
  cases. The intercept is unpenalized and the loss is a sum. The validator
  checks that `Xcᵀ·Xc + lam·I` has a condition number `<= 1e6`.
- [x] B3 `#5` `softmax-regression-gradient-descent`: PL.
- [x] B4 `#6` `elastic-net-gradient-descent`: PL. `sign(0) = 0` subgradient.
- [x] B5 `#7` `linear-svm-pegasos`: PL+RI. The sample order is an input; the
  subgradient at margin exactly 1 is pinned.
- [x] B6 `#8` `perceptron-learning-rule`: PL. Fixed pass order and epochs;
  `sign(0)` pinned.
- [x] B7 `#13` `multinomial-naive-bayes`: F. Laplace `alpha`; return the
  log-posteriors or labels; argmax ties go to the smallest class.
- [x] B8 `#14` `matrix-factorization-gradient-descent`: RI+PL. `U, V` are
  given; full-batch updates over the observed entries only.
- [x] B9 `#15` `adaboost-one-round`: F+TB. Stumps at midpoints, both
  polarities; errors within 1e-9 tie, then lowest feature, threshold, and +1
  first. The validator brute-forces that the best error is `>= 1e-3`.

### Wave C: evaluation and data handling (wave gates ✅ 2026-10-31)

Wave gates:

- `seed` and `audit` ALL CONSISTENT (1218 problems)
- `make check` green (577 tests; 17295/17295 cases); `check_db` OK
- Real server: all canonicals and numpy variants scored full marks. The
  reservoir variant returns a live numpy view that later calls mutate, and it
  passes, confirming the `_snapshot` fix on a second class problem. A
  per-batch-averaging `WeightedMetrics` scored 5/11.
- Pages returned 200; the collection shows 36.

Generators: `scratchpad/ml-coding/gen_{binmetrics,mcprf,streammetrics,skfold,scaler,reservoir,wsample,gradcheck}.py`.

Notes:

- **Suite size.** C3's first draft wrote 6.2 MB of cases (99 batches of
  1000), so it was cut to 5 batches (694 KB). C6 is 1.3 MB: 10k adds in the
  repo's `indent=2` JSON.
- **C8's relative error for a correct gradient is rounding noise** (about
  1e-11 to 1e-10). The statement says so, and the judge's absolute 1e-9
  covers it. `mlgen.vet` gained an `alt_tol` option, and C8 uses (1e-7, 1e-10)
  instead of the default (1e-9, 1e-12), still 10x inside the judge.
- **C7** has an all-underflow hidden case (weights near 1e-4) that breaks
  `u ** (1/w)`. **C8** has rows aligned with `w` (|z| about 800) that break a
  naive `log(1 + exp(z))`.

- [x] C1 `#16b` `binary-classification-metrics`: precision, recall and F1 at
  a threshold; `0/0 = 0`.
- [x] C2 `#17` `multiclass-precision-recall-f1`: macro and micro averages;
  `0/0 = 0`.
- [x] C3 `#18` `streaming-weighted-metrics`: CL, `update(batch)` /
  `result()`.
- [x] C4 `#19` `stratified-k-fold-indices`: F+RI. The permutation is an
  input.
- [x] C5 `#20` `standard-scaler-and-one-hot`: fit on train, transform test;
  missing values and unseen categories pinned.
- [x] C6 `#21` `reservoir-sampling`: RI. The uniform draws are an input.
- [x] C7 `#21b` `weighted-sampling-without-replacement`: RI.
- [x] C8 `#22` `gradient-check-finite-differences`: F. Central differences
  on a fixed loss; return the relative error.

### Wave D: neural-network building blocks (wave gates ✅ 2026-10-31)

Wave gates:

- `seed` and `audit` ALL CONSISTENT (1228 problems)
- `make check` green (577 tests; 17405/17405 cases); `check_db` OK
- Real server: every canonical, plus a numpy variant per problem returning
  arrays and tuples, scored full marks. D10's untouched starter scored 1/11:
  it passes only example 2, which avoids all seven bugs by design.
- Pages returned 200; the collection shows 46. D10's page renders the buggy
  starter in the editor.

Generators: `scratchpad/ml-coding/gen_{gelu,dense,batchnorm,conv2d,maxpool,cosinelr,gradclip,padbatch,quant,debugloop}.py`.

Notes:

- **The audit's "any order" heuristic reads input prose too.** D6's "steps
  can come in any order" tripped it, even though the answer order is fixed.
  The statement now says "not necessarily sorted".
- **D3 batch norm** has a hidden large-mean, tiny-spread case (values near
  2000 that differ by 0.01). The one-pass variance is off by 8.5e-6
  relative, so it fails, while honest methods agree to 4e-9. That case
  needed `alt_tol=(1e-8, 1e-11)`; near 9000 the honest methods differed by
  3.5e-8, too close to the judge, so the case was moved to 2000.
- **D9's margin check** (exact `Fraction` of `x / scale`) caught two
  *natural* near-ties: `3.5 / (7/255)` and `0.7 / (3/255)` are exact
  half-integers in exact arithmetic but not in floating point. Inputs moved.
  The exact ties all use power-of-two scales.
- **D10's vet** runs each planted bug alone, with the other six fixed, plus
  the real starter file. The naive-log-loss bug is the hidden-only one,
  caught by a separable huge-margin case where `0 · log(0)` gives NaN.
- PyTorch's clip coefficient `maxNorm / (norm + 1e-6)` differs from D7's
  `maxNorm / norm` by at most ~1e-7 relative, inside the judge, so either is
  accepted.

- [x] D1 `#24` `gelu-and-stable-sigmoid`: F; exact-`erf` GELU; the
  forward pass and its derivative.
- [x] D2 `#25` `dense-layer-backward`: LG → `{dX, dW, db}`.
- [x] D3 `#27b` `batch-norm-training-forward-backward`: LG.
- [x] D4 `#29` `conv2d-stride-padding`: F.
- [x] D5 `#29b` `max-pool-forward-backward`: F+TB (an argmax tie goes to the
  first position).
- [x] D6 `#31` `cosine-warmup-lr-schedule`: F.
- [x] D7 `#31b` `gradient-clipping-by-global-norm`: F.
- [x] D8 `#33` `pad-batch-and-attention-mask`: F.
- [x] D9 `#35` `int8-affine-quantization`: F+TB. Round half to even, then
  clip.
- [x] D10 `#36` `debug-broken-training-loop`: the starter is the buggy loop.

### Wave E: transformers and LLMs (wave gates ✅ 2026-10-31)

Wave gates:

- `seed` and `audit` ALL CONSISTENT (1240 problems)
- `make check` green (577 tests; 17537/17537 cases); `check_db` OK
- Real server: every canonical scored full marks, and so did a numpy variant
  per problem returning arrays, numpy scalars, and numpy ints under exact
  compare (E10). Wrong submissions: GQA with `h % numKvHeads` scored 4/11,
  RoPE with the half layout only 7/11, and speculative decoding with argmax
  3/11.
- Pages returned 200 (E12's `object` parameter renders); the collection
  shows 58.

Generators: `scratchpad/ml-coding/gen_{gqa,rope,sinpe,tfidf,lora,infonce,dpo,grpo,moe,specdec,cfg,gpt2}.py`.

Notes:

- **E8 shipped as one problem, `grpo-clipped-objective`**, covering both the
  PPO clip and GRPO advantages; the todo named two slugs. The advantages use
  the sample std plus 1e-4 (TRL / `torch.std`).
- **E9 has no noise term.** Noisy gating would only add an input matrix to
  the logits; capacity with token dropping is the substance instead. Exact
  logit ties appear only with integer-valued X and Wg, which every
  implementation computes exactly.
- **E6's gradient oracle is complex-step differentiation**
  (`Im f(x + ih) / h`, h = 1e-30), exact to rounding and independent of the
  analytic derivation.
- **E7 tie check:** an exact reward tie is allowed when both float
  subtractions are exact (x − x always is), not only for dyadic inputs.
- **E10's first suite was 1.9 MB.** Two 1000-wide tables at k = 16 in
  indent-2 JSON; cut to V = 1000 at k = 3 and V = 300 at k = 16 (899 KB).
- **An example explanation was wrong (E11).** The ratio was miscomputed by
  hand; the outputs were right. Example arithmetic in prose now gets checked
  with python before it ships.

- [x] E1 `#39` `grouped-query-attention`: F.
- [x] E2 `#41` `rotary-position-embedding`: F.
- [x] E3 `#41b` `sinusoidal-positional-encoding`: F.
- [x] E4 `#45` `tf-idf-cosine-retrieval`: F+TB.
- [x] E5 `#46` `lora-forward-and-merge`: F.
- [x] E6 `#47` `info-nce-contrastive-loss`: F/LG.
- [x] E7 `#48` `dpo-loss`: F (log-probs given).
- [x] E8 `#48b` `ppo-clipped-objective` / `grpo-advantages`: F.
- [x] E9 `#49` `moe-top-k-gating`: F+RI.
- [x] E10 `#50` `speculative-decoding-acceptance`: RI.
- [x] E11 `#51` `classifier-free-guidance`: F (small; maybe fold into E10's wave).
- [x] E12 `#53` `gpt2-block-forward`: F (d ≤ 16).

### Wave F: vision, RL, agentic, linear algebra (wave gates ✅ 2026-10-31)

Wave gates:

- `seed` and `audit` ALL CONSISTENT (1249 problems)
- `make check` green (577 tests; 17636/17636 cases); `check_db` OK
- Real server: every canonical scored 11/11, and so did an independent
  variant per problem (numpy returns where natural; the generators'
  alternates for the three plain-Python ones). Wrong submissions:
  - asymmetric bilinear scored 6/11
  - in-place value iteration 6/11
  - Q-learning that bootstraps past `done` 7/11
  - `true` counted as an integer 6/11
  - knapsack-style memory trimming 7/11
  - no idempotency 1/11
  - in-place Jacobi 6/11
  - Stability-only bugs failed exactly their one hidden case: one-pass
    covariance 10/11, the naive quadratic eigenvalues 10/11.
- Pages returned 200 (nested statement lists render); the collection
  shows 67.

Generators: `scratchpad/ml-coding/gen_{bilinear,valueiter,qlearn,toolargs,convmem,idem,cov,jacobi,eig2}.py`.

Notes:

- **The agentic three are plain Python** (no numpy needed) but carry the
  `machine-learning` tag like the rest of the collection. Two are class
  problems.
- **Near-tie promises:**
  - Value iteration promises that no sweep's change sits within 1e-9 of
    theta, and that a state's two best actions either differ by more than
    1e-9 or have identical outcomes.
  - Q-learning promises that only never-updated actions tie.
  - Jacobi/Gauss-Seidel promises no iteration's change within 1e-9 of tol.
  - The 2×2 eigen problem promises an eigen-gap ≥ 1e-6 and v1[0] ≥ 1e-6
    when b ≠ 0, so eigh-plus-sign-fix answers are well defined.
  - Generators vet all of these (`margin_check`, `separation_check`).
- **Examples were tuned to expose bugs:**
  - At α = 0.5, swapping α and 1 − α is invisible.
  - At |x| ≈ 2, relative-change stopping looks the same as absolute, so the
    Jacobi examples converge to [20, 30].
  - The 2-norm stopping bug needs a 3×3 system.
  - The no-constant-column-rule bug needs a constant column whose float mean
    is not exact: three copies of 0.1.
- **The covariance spread promise was dropped:** centering is exact, so the
  two-pass canonical matches exact rational arithmetic even at a 1e8
  offset. The canonical centers a constant column exactly, so its
  covariance prints as 0, not 3e-34.
- **One example explanation was wrong before shipping and was fixed**: the
  memory problem said 85 tokens were left where it should have said 65.
  Re-deriving the trace caught it. Value iteration's "sweep 129" was
  re-derived too and is correct; the naive estimate of 132 ignores the head
  start from the first sweeps.

- [x] F1 `#55` `bilinear-image-resize` (or a Gaussian blur): F.
- [x] F2 `#56` `value-iteration`: F.
- [x] F3 `#57` `q-learning-updates`: RI (the episodes are inputs).
- [x] F4–F6 `#58` agentic, plain Python (no numpy): a tool-argument
  validator, a sliding-window conversation memory (CL), retry with
  idempotency keys (CL). Shipped as `validate-tool-call-arguments`,
  `conversation-memory-window` (CL) and `idempotency-key-retries` (CL).
- [x] F7–F9 `#59` linear algebra, a handful: covariance matrix, Jacobi
  solver, 2×2 eigen. Shipped as `covariance-and-correlation`,
  `jacobi-gauss-seidel-solver` and `symmetric-2x2-eigen`.

### Wave G: 🟡 rows (reframed; each loses part of the original point) (wave gates ✅ 2026-10-31)

Wave gates:

- `seed` and `audit` ALL CONSISTENT (1251 problems)
- `make check` green (577 tests; 17658/17658 cases); `check_db` OK
- Real server: both canonicals scored 11/11. So did a micrograd-style
  object-API autograd (recursive topological sort, which handles the
  453-deep chain inside the default recursion limit) and a numpy merge.
  Wrong submissions: overwritten gradient accumulation scored 1/11, and the
  unshifted `exp(m)` merge overflowed on exactly the two large-score hidden
  cases (9/11).
- Pages returned 200 (the op table renders); the collection shows 69.

Generators: `scratchpad/ml-coding/gen_{autograd,softmerge}.py`.

Notes:

- **G1's alternate is forward-mode** (tangents seeded at every node, O(N²)),
  with derivative formulas written differently (1/cosh², e^−|x|/(1+e^−|x|)²).
- **First random DAGs were mostly dead:** only 1–3 of 25 nodes had nonzero
  gradients. Inputs now favour nodes with no users yet, and every dangling
  node is folded into the output, so 361 of 500 have nonzero gradients.
  The fold must fit inside the 500-node cap.
- **Gradient magnitudes:** the diamond chain (3 users per level, 3^40 paths)
  and the 450-deep chain were rebuilt so gradients stay O(1–100), not
  1e-13, where everything passes on the absolute tolerance.
- **pow domain:** `0 ** p` is allowed only for p = 0 or p ≥ 1, because a
  smaller p has an infinite derivative. pow′ is 0 when p = 0. The canonical
  only missed this because it skips zero-gradient nodes.
- **G2's alternate is plain attention** over the raw scores, values and mask
  each hidden case was cut from, so the merge is checked against the thing
  it replaces. The first full-size case was 4.3 MB (indent-2 floats). It
  was cut to 60 queries × ≤256 keys × d = 16, and the suite is now 754 KB.

Beyond the plan (optional, each is its own decision):

- #39's other attention variants (sliding-window, linear, cross)
- #57's REINFORCE
- #58's permission-aware tool registry and bounded tool-use loop

- [x] G1 `#34` `autograd-on-a-graph`: the expression graph as a JSON node
  list → the forward value and every node's gradient.
- [x] G2 `#52` `merge-partial-softmax-blocks`: the flash-attention online
  softmax step.
- [x] G3 `#28` dropout (mask given) and `#32` init (std/bound only):
  **skipped** (2026-10-31). With the randomness pinned, each comes down to a
  one-line scaling check.

Not doable: `#60`–`#62` (custom judge, torch, not code).

## 3. Hint quality gate: not needed for ML problems (owner, 2026-10-31)

The owner said ML problems need no hints. New ones ship without them, so there
is nothing to audit. If that changes, the old plan was
`scripts/improve_hints.py audit` scoped to the ML slugs (it needs the local
Qwen server, `/home/arman/claude_workspace/qwen/run.sh`), then
`fix --from-report` on the flagged ones.

## 4. Security-review follow-ups

These are low severity and **predate** this work. Each one touches
`app/executor/`, so run the `executor-security-reviewer` again after the change.

- [ ] **F3: a tampered `result.json` gives a 500.**
  - `sandbox.read_results` catches only `ValueError`. A 200k-deep `returned`
    raises `RecursionError`; catch it too.
  - Normalize each outcome in `subprocess_executor` before use:
    - `status` ∈ {ok, error, timeout}
    - `time_ms` a finite number or `None`
    - `error` and `stdout` strings
  - A solution can rewrite the file from an `atexit` handler. It can never
    cause a false pass, only a crash.
- [ ] **F5:** wrap each per-test call in the harness's `main()` and
  `_run_class_problem` in `try/except BaseException` that disarms the timer and
  records a timeout or error. A SIGALRM landing inside a `finally` currently
  kills the harness, and every result is lost.
- [ ] **F7: make `harness._plain` always round-trip** (`json.loads(json.dumps(…))`),
  so the harness owns plain data. Today a `dict` subclass's `items()` can run user
  code at write time, with no alarm. The class path already does this
  (`_snapshot`, 2026-10-31), so the simplest fix is to call `_snapshot` in
  `_run_one` and delete `_plain`. The reviewer measured 1.5–2.4 µs per call.
  The function path also aliases across tests:
  `acc = []; def f(x): acc.append(x); return acc` grades test 1 on `[1, 2]`. **Measure first** on the biggest suites
  (`sliding-window-maximum`, about 4.5 MB of cases): the extra decode is charged
  to the solver's time.
- [ ] **F11: `_write_results` and `_snapshot` use different JSON encoders.**
  `_snapshot` uses the C encoder (about 10,000 levels deep). `json.dump` in
  `_write_results._attempt` uses the pure-Python encoder, which hits the
  recursion limit at about 1,000 levels. `_attempt` catches only `OSError`, so
  a return nested about 1,400 deep makes every test report "the run was
  stopped", including tests that passed. It fails closed, and HEAD behaves the
  same. Fix: write with `f.write(json.dumps({"results": results}))`, and catch
  `(OSError, ValueError, TypeError, RecursionError, MemoryError)` so the
  degradation ladder runs. (Reviewer finding 1, 2026-10-31.)
- [ ] **F9:** hash-pin numpy in `infra/runner.Dockerfile`
  (`--require-hashes` against `numpy==<x> --hash=sha256:…`).
- [ ] **F10:** the local `lootcode-runner` image predates numpy, so with
  `EXECUTOR_BACKEND=docker` every numpy submission fails (it fails closed).
  - **Ask before rebuilding.** It's the owner's image:
    `docker build -f infra/runner.Dockerfile -t lootcode-runner .`
  - Then add a docker-gated test in `tests/test_sandbox.py` that imports numpy
    inside `settings.DOCKER_IMAGE`.

## 5. Commit ✅ done 2026-11-01

Committed as four commits: ML infra (numpy sandbox, `close` compare,
`machine-learning` tag, docs), KaTeX math rendering, the 69 problems + the
`ml-coding` collection, and the 🤖 ML Coding link in the top nav. The
"Not part of it" files below were handled separately: `house-robber-iii` was
committed on its own and `ml_problems.txt` is gitignored (owner, 2026-11-01);
the two big `cases.json` edits and the `.bak` are still uncommitted. The plan
as written:

Stage **explicitly**, never `git add -A` / `commit -a` (CLAUDE.md). These belong
to this work:

```
.claude/skills/canonical-tags/SKILL.md  CLAUDE.md  constraints.txt  requirements.txt
app/executor/__init__.py  app/executor/harness.py  app/executor/sandbox.py
app/llm/fill_in.py  app/llm/generator.py  app/llm/problem_prompt.txt  app/models.py
app/problem_spec.py  app/problem_validation.py  app/routers/admin_forms.py  app/tags.py
scripts/audit.py  scripts/verify_json.py  infra/runner.Dockerfile
docs/ai-analysis.md  docs/code-execution.md  docs/design-problems.md  docs/ml-coding-plan.md
docs/ml-coding-problem-bank.md  docs/ml-coding-todo.md
specs/problem-authoring-guidelines.md  specs/problem-schema.md  specs/tags.md
tests/test_compare.py  tests/test_executor.py  tests/test_tags.py
content/collections/ml-coding.json
content/problems/pairwise-ranker-i-loss-and-gradient/
content/problems/pairwise-ranker-ii-training/
content/problems/softmax-cross-entropy-loss-and-gradient/
content/problems/k-means-from-given-centroids/
content/problems/kv-cache-attention/
content/problems/roc-auc/
# Phase 3, Wave G
content/problems/autograd-on-a-graph/
content/problems/merge-partial-softmax-blocks/
# Phase 3, Wave F
content/problems/bilinear-image-resize/
content/problems/value-iteration/
content/problems/q-learning-updates/
content/problems/validate-tool-call-arguments/
content/problems/conversation-memory-window/
content/problems/idempotency-key-retries/
content/problems/covariance-and-correlation/
content/problems/jacobi-gauss-seidel-solver/
content/problems/symmetric-2x2-eigen/
# Phase 3, Wave E
content/problems/grouped-query-attention/
content/problems/rotary-position-embedding/
content/problems/sinusoidal-positional-encoding/
content/problems/tf-idf-cosine-retrieval/
content/problems/lora-forward-and-merge/
content/problems/info-nce-contrastive-loss/
content/problems/dpo-loss/
content/problems/grpo-clipped-objective/
content/problems/moe-top-k-gating/
content/problems/speculative-decoding-acceptance/
content/problems/classifier-free-guidance/
content/problems/gpt2-block-forward/
# Phase 3, Wave D
content/problems/gelu-and-stable-sigmoid/
content/problems/dense-layer-backward/
content/problems/batch-norm-training-forward-backward/
content/problems/conv2d-stride-padding/
content/problems/max-pool-forward-backward/
content/problems/cosine-warmup-lr-schedule/
content/problems/gradient-clipping-by-global-norm/
content/problems/pad-batch-and-attention-mask/
content/problems/int8-affine-quantization/
content/problems/debug-broken-training-loop/
# Phase 3, Wave C
content/problems/binary-classification-metrics/
content/problems/multiclass-precision-recall-f1/
content/problems/streaming-weighted-metrics/
content/problems/stratified-k-fold-indices/
content/problems/standard-scaler-and-one-hot/
content/problems/reservoir-sampling/
content/problems/weighted-sampling-without-replacement/
content/problems/gradient-check-finite-differences/
# Phase 3, Wave B
content/problems/linear-regression-gradient-descent/
content/problems/ridge-regression-closed-form/
content/problems/softmax-regression-gradient-descent/
content/problems/elastic-net-gradient-descent/
content/problems/linear-svm-pegasos/
content/problems/perceptron-learning-rule/
content/problems/multinomial-naive-bayes/
content/problems/matrix-factorization-gradient-descent/
content/problems/adaboost-one-round/
# Phase 3, Wave A
content/problems/logistic-regression-gradient-descent/
content/problems/scaled-dot-product-attention/
content/problems/multi-head-causal-self-attention/
content/problems/layer-norm-forward-and-backward/
content/problems/non-maximum-suppression/
content/problems/k-nearest-neighbors-classifier/
content/problems/beam-search-decoding/
content/problems/bpe-tokenizer/
content/problems/top-k-top-p-sampling/
content/problems/two-layer-mlp-backprop/
content/problems/adam-optimizer/
content/problems/principal-component-analysis/
content/problems/decision-tree-best-split/
```

The harness `_snapshot` fix (in `app/executor/harness.py` and
`tests/test_executor.py`, both already listed) could go in its own commit.

**Not part of it:** these were already modified before this work began. Leave
them alone unless the owner says otherwise:

- `content/problems/house-robber-iii/` (problem.md, cases.json, `assets/`)
- `content/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/tests/cases.json`
- `content/problems/sliding-window-maximum/tests/cases.json`
- `.claude/settings.local.json.bak`
- `ml_problems.txt` (the brief): the owner decides whether it gets committed.

Suggested split: (1) infra + judge + tests, (2) tag + docs, (3) content +
collection.

## 6. Later: each needs an owner decision first

- ~~**KaTeX math rendering**~~ — **done 2026-11-01** (`docs/math-in-statements.md`).
  Seven statements were converted to LaTeX as the pilot: `adam-optimizer`,
  `softmax-cross-entropy-loss-and-gradient`, `scaled-dot-product-attention`,
  `batch-norm-training-forward-backward`, `layer-norm-forward-and-backward`,
  `cosine-warmup-lr-schedule`, `dpo-loss`. The other 58 ML statements with a
  formula followed the same day, so all 65 now use LaTeX (1,204 formulas). Four
  have no formulas and were left alone: `bpe-tokenizer`,
  `validate-tool-call-arguments`, `conversation-memory-window`,
  `idempotency-key-retries`. Only the prose above `## Constraints` changed;
  constraints and examples are byte-identical. All 69 pages were checked in
  headless Chrome at 1100 and 1500 px: every formula typesets, nothing scrolls
  sideways. Originals: `scratchpad/latex-originals/` and
  `scratchpad/latex-pilot-originals/` (gitignored). The conversion found one
  trap: a `$$` block indented 3 spaces inside a numbered list rendered as raw
  TeX, so `check_math.py` now also fails on unwrapped TeX.
- **`compare: "custom"`** (a property judge, e.g. "accept if L(w) ≤ L* + ε").
  This would unlock "train however you like" problems and the deferred
  `getRandom`/`serialize` design problems. The checker is code, so it needs the
  trust model ICF chose (ADR 0003).
- **PyTorch:** out for now. The CUDA build needs about 4 GB of address space just
  to import.
- **Clean-up:** the real-server tests created guest users:
  `4d2bcbecd7284c9295d7179157d07e0f` (3 submissions), possibly one more from
  the startup probe, and one more on 2026-10-31 (about 20 submissions across softmax, k-means, KV cache and ROC-AUC, plus 28 for Wave A; its id is
  in `scratchpad/ml-coding/realrun/cookies.txt`). They are harmless. Delete them only if the owner
  wants, and only after backing up all three `lootcode.db*` files.
