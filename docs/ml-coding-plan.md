# ML coding problems: feasibility and plan

**Status (2026-10-30): decisions made, Phases 0–1 done, first problems shipped.**
**What's left, and how to resume it: [`ml-coding-todo.md`](ml-coding-todo.md).**
The owner chose: `compare: "close"`; problems stored in `content/problems/`; a new
canonical `machine-learning` tag **and** an `ml-coding` collection; no PyTorch; and
the ranking problem as a Part I / Part II pair. Implemented:

- **Phase 0 (infra):** numpy in `requirements.txt` / `constraints.txt` /
  `infra/runner.Dockerfile`; `sandbox.SINGLE_THREAD_ENV` on both backends.
  Reviewed by `executor-security-reviewer` (approved; its fixes are applied).
- **Phase 1 (judge):** `compare: "close"` (floats within rel `1e-6` / abs `1e-9`,
  ints exact, overflow-safe); the harness converts returned numpy values
  (`harness._plain`).
- **Content:** `pairwise-ranker-i-loss-and-gradient` and
  `pairwise-ranker-ii-training` (11 vetted cases each), plus the collection. The
  rest of the Phase 2 pilot (softmax + CE, k-means, KV cache, ROC-AUC) is not
  built yet.

The authoring rules from §5 now live in the "Machine-learning problems" section of
`specs/problem-authoring-guidelines.md`. Everything below is the original proposal,
kept for its reasoning. The problem inventory
is in the companion file **[`ml-coding-problem-bank.md`](ml-coding-problem-bank.md)**
(62 problems, each with sources and a fit verdict).

---

## TL;DR: answers to your four questions

1. **Are there collections of these problems?** Yes, and there are a lot of them. The
   best sources are Deep-ML (an open bank of 100+ numpy problems, judged
   LeetCode-style), the *AIMLInterviews* ML-coding list (41 problems with company
   tags), TorchCode (41 PyTorch problems with interview-frequency ratings), and
   company-attributed reports from PracHub, Blind and candidate write-ups. After
   de-duplication: **62 distinct problems**, in the [bank](ml-coding-problem-bank.md).
   The perennials are k-means, kNN, linear and logistic regression, stable
   softmax + cross-entropy, MLP backprop, attention, IoU/NMS and AUC. The LLM-era
   additions are KV cache, top-k/top-p sampling, beam search, BPE, LoRA and DPO.

2. **Do they fit lootcode's framework as asked?** **Not as-is**, but the gaps are
   small, and none of them touches the architecture. There are four:
   - **G1 (infra):** numpy isn't installed in the sandbox. Even once installed, it
     **crashes on import under the sandbox's memory cap** (measured; see below).
     Fixing it takes one environment variable.
   - **G2 (judge):** the judge compares with exact `==`. Three *correct*
     implementations of your ranking problem were bit-identical on only **9 of
     200** random datasets.
   - **G3 (judge):** a numpy array return value is rejected as "not JSON-serializable".
   - **G4 (problem shape):** "learn the `w` that minimizes L" **has no single right
     answer**. Your own example data is linearly separable, so the loss only
     reaches 0 as ‖w‖ → ∞. The `w` you return depends on your learning rate, step
     count and initialization. This is the one gap that needs a reframing rather
     than plumbing.

3. **Is there a variant that keeps ~90% and fits?** **Yes.** Your proposal
   (return `[loss, ∇loss]` and skip the loop) works and keeps about 85–90% of the
   problem. A second variant keeps about 95%: **keep the training loop but pin the
   procedure** (start at `w = 0`, `steps` full-batch updates `w ← w − lr·∇L`, with
   `lr` and `steps` as inputs). That makes the trajectory deterministic, and
   independent correct implementations agree to within 4.4e-16. Deep-ML does
   exactly this. I recommend publishing them as a pair, **Part 1 (loss & gradient)
   and Part 2 (train)**. A worked example with real numbers is in
   [§3.3](#33-worked-example-your-ranking-problem).

4. **Does it work for most of the problems found?** **Yes: 55 of 62 fit cleanly
   (89%), 4 more fit partially, and 3 don't fit.** The loss-and-gradient idea
   specifically is the right tool for the "training" problems, which are about a
   quarter of the bank. Most of the rest (36 of 62) are already pure functions
   (attention, metrics, conv2d, norms, sampling distributions, DPO loss…) and need
   only the infra fixes. The remainder needs one of two other small reframings:
   *pass the randomness in as an input* (k-means initial centroids, dropout masks,
   uniform draws), or *use the existing class kind* (KV cache, optimizers, streaming
   metrics). The 3 that don't fit are "train however you like and hit X accuracy"
   (needs a custom judge), PyTorch-only questions, and notebook/visual work.

---

## 1. What's out there

Full list with per-problem sources: **[ml-coding-problem-bank.md](ml-coding-problem-bank.md)**.

| Source | Size | How it judges (relevant to us) |
|--------|------|--------------------------------|
| [Deep-ML](https://github.com/Open-Deep-ML/DML-OpenProblem) | 100+ numpy problems | LeetCode-style test cases. **It hit the same problems we have and solved them the same way:** the statement says "round to 4 decimals", the hyperparameters are inputs (`alpha`, `iterations`), and k-means takes `initial_centroids` as an input. License is "educational use only", so we write our own statements. |
| [AIMLInterviews: ML coding](https://github.com/alirezadir/Machine-Learning-Interviews/blob/main/src/MLC/ml-coding.md) | 41 problems | Company tags (Apple, Meta, Google, Amazon, Uber, LinkedIn, Anthropic, OpenAI, DeepMind, Perplexity, Databricks…). Grouped into classic ML / LM / GenAI / agentic. |
| [TorchCode](https://huggingface.co/spaces/duoan/TorchCode/blob/main/README.md) | 41 PyTorch problems | `torch.allclose` (a tolerance compare) plus gradient-flow checks. Rated by interview frequency. |
| [PracHub](https://prachub.com/positions/software-engineer/categories/machine-learning), [AI Eng. Insider](https://aiengineeringinsider.substack.com/p/105-maang-ai-engineer-interview-questions), Blind, [Yuan Meng](https://www.yuan-meng.com/posts/mle_interviews_2.0/) | reports | Company-attributed questions: Meta attention / k-means, Amazon stable softmax + attention, OpenAI autograd, NVIDIA int8 quantization, Microsoft beam search, Apple cosine similarity, frontier-lab KV cache / LoRA / debugging rounds. |

Two things matter for the format. First, interviews at frontier labs increasingly
include **debugging rounds** (fix this broken training loop). Those fit lootcode
for free, because the starter code *is* the bug. Second, "numpy allowed, no
sklearn" is the norm reported for classic ML coding rounds, which matches your
brief.

---

## 2. Does it fit lootcode's framework today?

What the framework assumes (`specs/problem-schema.md`, `app/executor/`):

- The solver defines one top-level function (or a `kind: "class"` design class).
- Each test is a JSON `input` dict, and `expected` is a JSON value.
- The sandbox is a subprocess run with rlimits, using **the web app's own
  interpreter** (`sys.executable`). It gets a minimal environment.
- The return value is compared in the trusted parent with **exact structural
  `==`** (`exact` / `unordered` / `set_of_lists`).
- The canonical solution is the only oracle. Every input passes `validate_input`.

### The four gaps

| | Gap | Evidence | Fix | Size |
|-|-----|----------|-----|------|
| **G1** | numpy unavailable, and it **crashes on import** under the sandbox limits | Not in `requirements.txt`, not in `.venv`, not in `infra/runner.Dockerfile`. Probe (numpy 2.4.6, run with the real `sandbox._preexec` limits): the minimal env fails at 512 MB and at 256 MB with *"OpenBLAS error: Memory allocation still failed after 10 retries"*. With `OPENBLAS_NUM_THREADS=1` it **works**: import 42 ms, then a 300×300 matmul + solve in 10–20 ms. OpenBLAS sizes a buffer per core, and this box has 16 cores. | Pin numpy in `requirements.txt` / `constraints.txt` / the runner image. Add `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` to the sandbox env in `sandbox.py` (subprocess env dict + `-e` flags in `docker_command`). | Small, but `sandbox.py` is security-critical, so it needs the `executor-security-reviewer` |
| **G2** | Exact float compare | 200 random ranking datasets, 300 GD steps, 3 correct implementations (vectorized numpy; a different op order with a tanh-sigmoid; a pure-Python loop). Bit-identical on **9/200**. Worst difference: **4.4e-16**. Rounded to 4 or 6 decimals they agree on **200/200**. A numpy upgrade can also move the last bits of a stored `expected`. | **(a)** The house rounding convention ("return values rounded to 6 decimals"). 18 bank problems already do this, as does Deep-ML. **(b, recommended)** A new `compare: "close"` mode, see below. | (a) none · (b) small, judge-side only |
| **G3** | numpy return values aren't JSON-serializable | `harness._run_one` calls `json.dumps(returned)`. An `ndarray`, `np.float32` or `np.int64` fails as *"Return value is not JSON-serializable: ndarray"*. `np.float64` happens to pass because it subclasses `float`. | **(a)** The statement says "return a list (`.tolist()`)". **(b, recommended)** The harness converts recursively anything that has a `.tolist()` method, using duck typing, so the harness still imports nothing. Inputs need no change: JSON lists → `np.asarray(...)`, which is how your brief passes data anyway. | (b) small, but `harness.py` is security-critical, so it needs review |
| **G4** | "Learn the minimizer" has no unique answer | Your two example pairs are **linearly separable**: `w = [0,0,1]` gives margins 1 and 5, so L → 0 only as ‖w‖ → ∞. Gradient descent from 0 with lr 0.5 gives ‖w‖ = 2.8 / 4.4 / 6.1 and loss = 1e-2 / 1e-3 / 1e-4 after 100 / 1,000 / 10,000 steps. Any returned `w` is an artifact of lr, init and stopping, so there is no `expected` to store. | Reframe the problem: §3. | Content-only |

**Why `close` over rounding (G2).** Rounding works in practice (200/200 above), but
it has three costs. Every nested float must be rounded by the solver, which is
noise unrelated to ML. A true value sitting on a rounding boundary can still flip.
And tiny answers (a probability of 1e-9) round to 0 and stop being tested. The
`close` mode would compare recursively: numbers via `math.isclose(rel_tol=1e-6,
abs_tol=1e-9)`, lists element-wise with equal length, dicts with equal keys, and
`bool`/`str`/`None` exactly (a `bool` is *not* treated as a number). `NaN` is never
equal. A tolerance of 1e-6 is safe because wrong answers in this domain are off by
O(1) factors (a missing `1/N`, a sign, the wrong axis), about seven orders of
magnitude away from float noise. The mode lives in `_equal`
(`app/executor/__init__.py`), so it runs in the **trusted parent with no sandbox
change**. `compare` is a `String` column, so there is **no DB migration**. Every
place that lists compare modes needs a line:
`app/executor/__init__.py`, `app/problem_spec.py`, `app/problem_validation.py`,
`app/models.py`, `app/routers/admin_forms.py`, `app/llm/{fill_in,generator}.py`,
`app/llm/problem_prompt.txt`, `scripts/{audit,build_bank,verify_json}.py`,
`specs/problem-schema.md`, `specs/problem-authoring-guidelines.md`, plus tests.

### Smaller points

- **Math in statements.** *Done 2026-11-01:* KaTeX is vendored and
  `pymdownx.arithmatex` lifts `$…$` / `$$…$$` out before Markdown runs, so
  statements write formulas in LaTeX (`docs/math-in-statements.md`). Before
  that, v1 statements wrote them in Unicode inside code blocks
  (`L(w) = (1/N) Σᵢ log(1 + exp(−w·(x₁ⁱ − x₂ⁱ)))`). All ML statements with a
  formula were converted the same day.
- **Tags.** None of the 44 canonical tags is about ML, and the house rule is not to
  invent one inline. **Group them with a collection** (`content/collections/ml-coding.json`;
  collections are already a list filter) and tag each problem with whatever fits
  (`matrix`, `math`, `sorting`, `heap`…). Adding a `machine-learning` tag is a
  separate decision, because `app/tags.py` and `problem_prompt.txt` have to stay in sync.
- **Sizes.** Inputs are JSON, so keep matrices small (about 200×20 at most).
  Outputs count against the ~1 MB per-run result budget, summed over all tests.
  Return weights and losses, not predictions for large batches.
- **Validators** work unchanged (consistent shapes, finite values, ranges). The trap
  in CLAUDE.md ("the validator checks inputs, not the statement's promises about the
  answer") is *sharper* here. If a statement promises full rank, distinct
  eigenvalues or no equidistant points, the validator must enforce it, or the
  statement must pin a tie rule.
- **Speed.** numpy import costs about 40 ms once per run, not once per test.
  Negligible.
- **PyTorch** (for the 🟡/❌ rows). Probe: torch 2.5.1 (CUDA build) **fails to
  import** at 512 MB and at 2 GB of address space (*"failed to map segment from
  shared object"*). It imports at 4 GB in about 1 s, and it is 1.6 GB on disk. A
  CPU-only wheel is smaller, but it would still be a heavy dependency of the web
  app's own interpreter. **Recommendation: numpy only.** Most torch-phrased
  questions (attention, norms, LoRA, losses) translate to numpy without loss.

**Already fine as-is:** visible and hidden cases with weights; the canonical as
oracle (`seed.py`, `verify_bank.py`); the hint pipeline; `kind: "class"` for
stateful problems; per-problem `limits`; the duplicate checks.

---

## 3. The reframing

### 3.1 Your proposal: loss and gradient

`f(preferences, w) → [loss, grad]`. This is a pure function of its inputs, so it
is deterministic and gradeable with `close`.

- **Kept:** deriving `∇L`, which is the actual hard part and what interviewers
  grade. Also vectorization, shapes, and **numerical stability**. A hidden case
  with margin −800 makes the naive `log(1 + exp(−m))` return `inf`, while the
  stable `logaddexp(0, −m)` returns 800. That is measured, and it is graded
  automatically.
- **Lost:** the loop itself (about three lines), choosing lr / steps / stopping,
  and the "does it converge?" discussion.
- **Verdict: about 85–90% of the problem.**

### 3.2 Better: pin the training procedure (and ship both as Part 1 / Part 2)

`train_ranker(preferences, lr, steps) → w`. The statement fixes the procedure:
*start at `w = 0`; apply exactly `steps` full-batch updates `w ← w − lr·∇L(w)`,
where L is the **mean** over pairs; there is no bias term.* The trajectory is then
a deterministic function of the input. In the G2 probe, three independently written
implementations agreed to within 4.4e-16 after 300 steps. The candidate still
writes the loss, the gradient and the loop. Only the hyperparameters are dictated,
and they arrive as inputs, the way Deep-ML does it. **About 95%.**

I recommend shipping both as adjacent problems in the collection, "Pairwise Ranker
I: Loss & Gradient" and "Pairwise Ranker II: Training", like LeetCode's I/II pairs.
(One `kind: "class"` problem with `loss_and_grad` / `fit` / `weights` methods could
hold both, but two plain function problems are simpler to author and to grade
partially.)

### 3.3 Worked example: your ranking problem

The values below were computed with numpy 2.4.6 using the reference implementation
I would make canonical. JSON has no tuples, so each pair is a 2-element list.

**Part 1** (`ranking_loss_and_grad(preferences, w)`, returns `[loss, grad]`):

```jsonc
{ "name": "example-1",
  "input": { "preferences": [[[2.0, 1.0, 3.0], [1.0, 1.0, 2.0]],
                             [[1.0, 1.0, 2.0], [2.0, 2.0, -3.0]]],
             "w": [0.5, -0.5, 0.25] },
  "expected": [0.3194000437301364,
               [-0.04906058099964908, 0.11135006941265443, -0.7171609974755757]],
  "hidden": false }
```

**Part 2** (`train_ranker(preferences, lr, steps)`, returns `w`), on the same pairs with
`lr = 0.1, steps = 100`:
`[0.8121679467047354, -0.11611104444172111, 1.5088342133550618]`.

**Hidden-case families** (the same idea carries over to every LG/PL problem):
- `N = 1` and `d = 1`.
- An identical pair (`x₁ = x₂`): loss = log 2 and grad = 0 for any `w`.
- `w = 0`: loss is exactly log 2. Here the gradient is `[-0.0, 0.25, -1.5]`, and
  `-0.0` vs `0.0` is equal under both `exact` and `close`.
- `steps = 0`: returns the zero vector.
- The margin −800 stability case.
- A larger `N ≈ 200, d ≈ 10` case.

**Validator:** non-empty `preferences`; every vector has the same length `d ≥ 1`;
values are finite with |value| ≤ 10³; `len(w) = d`; `0 < lr ≤ 10`;
`0 ≤ steps ≤ 5000`.

### 3.4 The general patterns (used to classify the bank)

| Code | Pattern | Rule | Example |
|------|---------|------|---------|
| **F** | Pure function | Already deterministic, so it needs only the infra fixes. | attention, AUC, conv2d, DPO loss |
| **LG** | Loss & gradient | Return `[loss, grad]`, or `{"loss": …, "dW": …}` for several parameters. | logistic regression, dense-layer backward, MLP backprop |
| **PL** | Pinned loop | Init, lr, steps and update rule are pinned. Hyperparameters become inputs. | linear/logistic regression GD, perceptron |
| **RI** | Randomness as input | Pass the random parts in. **Never "seed + `np.random`"**: the answer would then depend on which RNG API the solver called, and in what order. | k-means `initial_centroids`, dropout mask, uniform `u` for top-p, SGD order |
| **CL** | Class kind | Stateful. Uses the existing design-problem machinery. | KV cache, Adam `step()`, streaming metrics |
| **TB** | Tie-break pinned | The statement fixes ties and sign conventions. | kNN vote ties, PCA eigenvector sign, NMS equal scores, int8 rounding mode |

The **debugging round** falls out for free: the starter is a buggy implementation,
and the tests describe correct behavior.

### 3.5 What reframing can't fix

"Train however you like" problems can only be graded by a **property** of the
answer: accept if `L(w_returned) ≤ L(w*) + ε`, or if held-out accuracy ≥ a
threshold. That needs a `compare: "custom"` checker. `specs/problem-schema.md`
already floats one for `getRandom` / `serialize` design problems, so one
mechanism would unlock both. The checker is code, though, so it raises the same
trust question ICF settled for its oracles (file-authored only, ADR 0003). **Not
proposed for v1.** The PL variant covers these problems well enough.

---

## 4. Does the modification generalize? (tally from the bank)

| Verdict | Count |
|---------|------:|
| ✅ Fits cleanly after the G1–G3 infra fixes | **55 / 62 (89%)** |
| 🟡 Fits, but the gradeable output can't check the problem's real point (dropout, weight init, autograd engine, flash attention) | 4 |
| ❌ Doesn't fit (free-form training, PyTorch-only, notebook/visual) | 3 |

Among the 55: **36 are pure functions** (F), **9** are mainly your loss-and-gradient
or pinned-loop pattern (LG/PL), **6** pass randomness in (RI), and **4** use the
class kind (CL). So the answer to Q4 is *yes, with one refinement*. The deviation
you proposed is exactly right for the training-type problems. Most of the other
problems never needed it, because they were deterministic all along and were only
blocked by the infra gaps (numpy, float compare, ndarray returns), which apply to
every problem here.

---

## 5. Proposed implementation plan (not started; for your go-ahead)

**Phase 0: infra** (core; `executor-security-reviewer` before merging)
- Pin numpy in `requirements.txt`, `constraints.txt` and `infra/runner.Dockerfile`,
  and install it into `.venv`.
- Set the single-threaded BLAS env in `sandbox.py`, for both backends. This is also
  right on its own merits: `RLIMIT_CPU` counts every thread, and threaded reductions
  change summation order from machine to machine.
- numpy doesn't widen the boundary, which is process-level (stdlib `ctypes` is
  already importable). Still, the review is mandatory for this file.
- Add a `tests/test_executor.py` case: a submission that imports numpy and does a
  matmul passes under the default limits.

**Phase 1: judge**
- `compare: "close"` across the 13 files listed in §2.
- `.tolist()` coercion in `harness.py` (security review).
- Spec and doc updates.
- `audit.py` must treat `close` like `exact` for its ordering checks.

**Phase 2: pilot, 6 problems that together exercise every pattern**, in a new
`ml-coding` collection:
- Ranker I (LG) and Ranker II (PL).
- Stable softmax + cross-entropy (F + stability cases).
- k-means with given centroids (RI + TB).
- KV cache (CL).
- ROC-AUC (F + TB).

Gate: `seed.py`, `verify_bank.py`, `audit.py`, `check_constraint_validators.py`,
**and the real server** (per CLAUDE.md, "done" means the real thing ran).

**Phase 3:** the rest of the bank, in waves of about 10, by bank section.

**Phase 4 (optional, separate decisions):** KaTeX math, a `machine-learning` tag,
`compare: "custom"`, PyTorch.

### Authoring rules for ML problems (to add to `specs/problem-authoring-guidelines.md`)

1. **Pin every degree of freedom:** init, lr, steps, mean vs. sum, bias term, `eps`,
   biased vs. unbiased variance, rounding mode, tie-breaks, sign conventions, and
   the empty-cluster rule.
2. **Randomness is an input.** Never "use seed 42".
3. **Second-implementation check before publishing.** Run an independently written
   solution with a different op order over every case. If it disagrees beyond the
   tolerance, the case is ill-conditioned, so drop it. This cheaply catches near-ties,
   ReLU-at-zero kinks and chaotic trajectories, which the canonical-only check
   cannot see.
4. **Stability cases** (huge logits or margins) whenever the statement says
   "numerically stable", or when it is the point of the question.
5. **Small inputs and small outputs** (JSON size; the ~1 MB result budget).
6. **The validator enforces the statement's promises about the answer** (full rank,
   distinct eigenvalues, no ties unless a tie rule is stated).
7. **Our own statements.** Deep-ML's license is "educational use only". Say
   "numpy and the standard library" (SciPy and sklearn aren't installed, so the
   statement matches reality).

### Decisions for you

1. **Float judge:** add `compare: "close"` (recommended), or use the existing
   "round to N decimals" convention with no judge change?
2. **Content root:** `content/problems/` (git-tracked; these would be our own
   statements) or `content/problems-extended/` (local; where recent batches went)?
   I lean towards `content/problems/`.
3. **Tag:** collection-only for now (recommended), or add `machine-learning` as the
   45th canonical tag?
4. **PyTorch:** keep it out for v1 (recommended)?
5. **Pilot list:** are the six above the right first set?

---

### How the numbers above were measured

The measurements used throwaway scripts in the session scratchpad. They ran
against an existing conda env (numpy 2.4.6 / Python 3.12; torch 2.5.1). **The
project and its `.venv` were not modified.** The sandbox limits were applied by
importing the real `app.executor.sandbox._preexec` and `nproc_limit`, with the
same minimal environment the executor uses.
