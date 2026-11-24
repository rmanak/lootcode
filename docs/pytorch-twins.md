# PyTorch twins of the numpy ML problems

A **twin** is a numpy ML problem again, in PyTorch, so the same exercise can be
practised in both frameworks. Twins are deliberate near-duplicates, kept **as
close to the numpy original as possible**, and the two share **one body of
tests**.

- **Slug.** `<numpy-slug>-pytorch`, in the same content root as the original.
- **Tags and collection.** The numpy tags plus `pytorch`, and the twin is listed
  in the `ml-coding-pytorch` collection (🔥 PyTorch in the nav), in the numpy
  study order. `pytorch` ⟺ `"runtime": "torch"` (`tests/test_tags.py`), and
  `ml-coding` holds only the numpy problems.
- **Link.** `torch.twin` in the twin's `meta.json` names the numpy slug. It lives
  inside the `torch` block because `write_problem_files` rebuilds `meta.json`
  from known fields, and a top-level key would vanish on the first admin edit.
  The problem page shows "Also in PyTorch →" and "Also as a numpy problem →"
  from it (`store.twin_of`).
- Graded by the PyTorch runtime (`docs/torch-runtime.md`). The twin's canonical
  is a live oracle: stored tests carry `expected: null`, and every run adds
  fresh random tests.

## What is the same, and what differs

| | numpy problem | twin |
|---|---|---|
| function and parameter names | `infoNCE(U, V, temperature)` | the same |
| shapes, constraints | as stated | **the same**; the statement is copied |
| input validator | `input_validator.py` | a byte-identical copy |
| stored tests | hand-curated + baked `gen-*` cases with `expected` | every numpy case, same name, weight and hidden flag, `expected: null`, except any `tests/twin.json` skips (inputs float32 cannot hold); plus optional twin-only `torch-*` cases |
| random tests | baked from `tests/generator.json` | drawn on **every run** from the same generator, or from the twin's own float32-scale one (`tests/twin.json`) |
| inputs | plain lists | numeric arrays become **float32** tensors (`int`/`bool` arrays as int64/bool; float64 for the 5 that say why); scalars and strings stay plain values |
| return | lists and numbers | the same structure, tensors in place of arrays, 0-dim tensors in place of numbers |
| hand-written gradients | yes (numpy has no autograd) | the same exercise. Nothing blocks autograd or the built-in that *is* the exercise (`F.layer_norm`); this is practice, so that's the solver's call |
| judging | `close`: rel 1e-6 / abs 1e-9 | allclose, mostly `rtol=1e-4`, `atol=1e-5` (see the table); shape and dtype exact |

**dtype: float32, as deep learning trains.** A twin is float32 unless the
*statement's own constraints* put the exercise out of float32's reach; only 5
of the 33 are float64, each saying why in a **Why float64?** paragraph
(see the table). float32 twins are judged at `rtol=1e-4`, `atol=1e-5` (the
tightest that held: `rtol=1e-5`, `atol=1e-6` where the cross-check stays below
0.25 at that setting; pixel-scale `atol=1e-2` for bilinear's 0–255 images).

Until 2026-11-23 most twins were float64. The numpy problems were built for
float64 and carry inputs that are fine there and meaningless in float32, and
the "same tests" rule moved the dtype instead of the inputs. Re-running every
cross-check in float32 showed three causes, and each has a fix that keeps
float32:

- **Generator ranges no network sees** (weights to ±10 or ±100, so attention
  scores reach thousands and softmax flips on float32 near-ties; batches of 2;
  rows of 2 features). The twin gets **its own generator** at float32 scale
  (activations ±3, weights ±0.5–1, batches ≥ 8), still inside the shared
  validator.
- **Stored cases float32 cannot represent** (mean 1000 with spread 0.05, a
  mean of 2000 with deviation 0.008, `lr` far past GD's stability bound,
  baked draws from the wide numpy generator). The twin **skips** them, and a
  `torch-*` case keeps the trap at float32 scale where one exists
  (`torch-large-mean-small-spread`: two-pass passes, one-pass `E[x²] − E[x]²`
  fails; `torch-confident-mistakes`: |z| past float32's `exp` overflow in 5
  steps).
- **A float64-sized tolerance**: `rtol=1e-5` is ~170 float32 ulps, too tight
  for iterative or long-reduction answers. Hence `rtol=1e-4`.

Both overrides live in `<twin>/tests/twin.json`, every entry with a `why`:

```json
{"generator": {"why": "...", "dims": {...}, "inputs": {...}},
 "skip": {"<numpy case name>": "why float32 cannot hold it"}}
```

It sits beside the cases, not in meta.json's `torch` block, because the runtime
keeps that block strict. `port` reads it (draws from the own generator must pass
the validator, 500 of them), and `tests/test_twins.py` pins it.

**Keep the oracle's own float32 accuracy in mind.** In the sandbox (one
thread) `F.batch_norm`'s float32 backward lost ~1e-4 of `dgamma` that the
multi-threaded path did not, so that canonical (like layer norm's) now
differentiates the explicit two-pass formula. And `check` measures the
canonical against float64 truth on a sample: a rare draw can still fail a
*correct* submission (one in 1000 layer-norm draws did, a 2-feature row), so
also grade a hand-written correct solution against a few thousand draws.

## How tests flow

```
                    <numpy>/tests/generator.json   (one generator, both sides)
                       │                        │
        bake ──────────┘                        └────────── port (copied into torch.inputs)
          │ draws → float32-rounded → numpy validator           │
          │ → numpy canonical → keep k with differing answers   │ the twin draws `random_tests`
          ▼                                                     ▼ fresh inputs on every run
  <numpy>/tests/cases.json  ─────────── port ─────────►  <twin>/tests/cases.json
  (expected = numpy canonical)                          (expected: null; the torch
                                                         canonical is the oracle)
```

- **numpy → twin (`port`).** Every numpy case, including the baked `gen-*`
  ones, becomes a twin case. The adversarial cases the numpy suite was built
  around (the stability traps, the edge shapes, the wrong answers it was
  hardened against) therefore guard the twin from day one. This is items 1 and 2
  of the torch-runtime authoring checklist.
- **twin → numpy (`bake`).** The generator is the twin's random-test source. For
  the numpy side, `bake` draws `-n` inputs from it and rounds every float the
  twin would hold as float32 to float32. A baked case is then the same test on
  both sides, bit for bit. `bake` keeps the `-k` draws whose *answers* differ
  most (greedy farthest-first over output statistics, within `--max-kb`) and
  stores them as hidden `gen-<seed>-<i>` cases with the numpy canonical's
  answers. A re-bake replaces them. This works for any numpy problem with a
  `tests/generator.json`, twin or not. Every draw must satisfy the validator,
  because the twin draws from the same generator live.
  `scripts/check_constraint_validators.py` holds every numpy generator to it
  (300 draws), as it already did for torch generators.
- **Cross-check (`check`).** The twin's canonical runs in the torch sandbox on
  every stored case plus `-n` generator draws. The numpy canonical (float64)
  runs on the same, float32-rounded inputs. The worst disagreement is reported
  in units of the twin's tolerance, `|t − n| / (atol + rtol·|n|)`. Below 0.5
  (the limit), a correct submission with a different op order is safe. Write
  the twin's canonical with **autograd and the library built-ins**: it is then
  independent of the numpy canonical's hand-derived math, so agreement is real
  evidence that both are right.

## Adding a twin

```bash
S=scripts/sync_twin_tests.py
# 1. A generator for the numpy problem, written from its validator's bounds
#    (uniform low/high ranges keep draws in bounds; see torch-runtime.md for
#    min_abs / step / at_least_one_per_row / randint "high": "<dim>", dim
#    expressions such as "D": "H*hd", and {"$dim": "H"} for a scalar like
#    numHeads). Size the dims for the OUTPUTS: one run's answers share a ~1 MB
#    result budget (check fails past 60% of it).
$EDITOR content/problems/<slug>/tests/generator.json
# 2. Bake random hidden cases into the numpy problem.
.venv/bin/python $S bake <slug> --write
# 3. Scaffold the twin.
.venv/bin/python $S scaffold <slug> --write
#    Then by hand:
#    - solution/solution.py: the reference, using autograd/built-ins freely;
#    - meta.json function.returns: "any[]" when the numpy answer is a list of
#      separate arrays, not one matrix;
#    - starters/python/solution.py, and the numpy one to match: a multi-line
#      Args/Returns docstring. Every input gets its type and its shape in
#      named dims (batch_size, seq_len, d_model, num_classes, ...); outputs get
#      their type only (list or single array/tensor, dtype, 0-dim for a
#      scalar), never a shape, which can give the answer away;
#    - a parameter that should stay a plain list (a kernel size [kH, kW]):
#      set its type back to the numpy one, e.g. "int[]";
#    - a ragged numpy float[][] (one gradient per parameter, one log-prob
#      list per completion): type it "Tensor[]" and draw it with $list
#      (share lengths between parallel lists); an any[] array (a 4-D conv
#      weight) may be typed "Tensor";
#    - problem.md: scaffold replaced the "You may use numpy" and "Answers are
#      accepted" paragraphs; fix anything else numpy-specific
#      (math.exp, OverflowError, "about 709" in float32, numpy.argmax).
#      After any meta edit (return type, dtypes) refresh the generated
#      paragraphs; --out-dtype when integer inputs give a float answer:
.venv/bin/python $S statement <slug> [--out-dtype float64] --write
# 4. Copy the tests across and cross-check.
.venv/bin/python $S port <slug> --write
.venv/bin/python $S check <slug>       # fails? read the worst inputs: a draw no
                                       # float32 model sees -> the twin's own
                                       # generator; a stored case float32 cannot
                                       # hold -> skip it (+ a torch-* stand-in);
                                       # both in tests/twin.json. float64 only if
                                       # the constraints themselves need it.
# 5. Hand-written solutions: one correct one passes, and the typical wrong ones
#    fail. Then `make check`.
```

**When the numpy problem changes** (new cases, a re-bake, a generator edit),
run `port <slug> --write`. `tests/test_twins.py` fails until you do. It pins:

- the contract;
- the byte-identical validator;
- the tags;
- the generator: the shared one, or the twin's own (its draws inside the
  validator);
- the ported cases, minus the skipped ones (each of which must exist);
- the collection order.

## The twins

| twin | dtype; tolerance; `tests/twin.json` | cross-check (× tolerance; float32 rows: worst of the stored cases + 3000 draws) |
|---|---|---|
| `info-nce-contrastive-loss-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.34 (float32 on the numpy inputs was 5×, at τ = 0.001) |
| `softmax-cross-entropy-loss-and-gradient-pytorch` | float32; rtol 1e-5, atol 1e-6 | 0.017 |
| `scaled-dot-product-attention-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.18 (float32 on the numpy inputs was 596×) |
| `layer-norm-forward-and-backward-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator, skips 1 | 0.27 (float32 on the numpy inputs was 1.5e5×). The reference differentiates the explicit two-pass formula: `F.layer_norm`'s fused backward returned -4e-7 for an exact 0 ) |
| `gelu-and-stable-sigmoid-pytorch` | float32; rtol 1e-5, atol 1e-6 | 0.25 |
| `dense-layer-backward-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.22 (float32 on the numpy inputs was 7×: `1 − tanh²`) |
| `sinusoidal-positional-encoding-pytorch` | int64 positions in, float64 out; rtol 1e-5, atol 1e-6 | 1e-5 (positions up to 1e5: float32 angles are off by ~4e-3) |
| `rotary-position-embedding-pytorch` | float64; rtol 1e-5, atol 1e-6 | 3e-5 |
| `multi-head-causal-self-attention-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.2 |
| `grouped-query-attention-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator, skips 1 | 0.22 |
| `distance-decay-attention-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator, skips 1 | 0.13 |
| `attention-backward-pass-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator, skips 4 | 0.2 |
| `batch-norm-training-forward-backward-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator, skips 5 | 0.44 |
| `max-pool-forward-backward-pytorch` | float32; rtol 1e-5, atol 1e-6 | 0.12 (a stored case with arbitrary decimals) |
| `label-smoothed-masked-cross-entropy-pytorch` | float32; rtol 1e-5, atol 1e-6 | 0.039 |
| `dpo-loss-pytorch` | float32; rtol 1e-5, atol 1e-6; own generator | 0.069 (log-probs on a 1/64 grid) |
| `grpo-clipped-objective-pytorch` | float32; rtol 1e-4, atol 1e-5; the three log-prob lists are `Tensor[]` (one tensor per completion, `$list` with `share`) | 0.043 |
| `conv2d-stride-padding-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator; `weight` is `Tensor` | 0.32 |
| `two-layer-mlp-backprop-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.15 |
| `lora-forward-and-merge-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.26 |
| `classifier-free-guidance-pytorch` | float32; rtol 1e-4, atol 1e-5 | 0.28 |
| `gradient-clipping-by-global-norm-pytorch` | float64; `grads` is `Tensor[]` (`$list`); rtol 1e-5, atol 1e-6 | 5e-11 |
| `pairwise-ranker-i-loss-and-gradient-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.017 |
| `kl-and-js-divergence-pytorch` | float32; rtol 1e-5, atol 1e-6 | 0.082 |
| `linear-regression-gradient-descent-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.057 |
| `logistic-regression-gradient-descent-pytorch` | float32; rtol 1e-4, atol 1e-5; skips 1 | 0.023 |
| `softmax-regression-gradient-descent-pytorch` | float32; rtol 1e-5, atol 1e-6 | 0.2 |
| `elastic-net-gradient-descent-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.12 |
| `pairwise-ranker-ii-training-pytorch` | float32; rtol 1e-5, atol 1e-6 | 0.12 |
| `bilinear-image-resize-pytorch` | float32; rtol 1e-4, atol 0.01 | 0.09 at a pixel-scale `atol` (float32 rounds a source coordinate by ~1e-5, a few thousandths of a pixel; at `atol=1e-5` that was 7×) |
| `covariance-and-correlation-pytorch` | float64; rtol 1e-5, atol 1e-6 | 2e-7. The generator draws a per-test offset up to 1e8 with spread down to 0.5, so the one-pass-variance trap comes up live |
| `int8-affine-quantization-pytorch` | float64 in; `zeroPoint` and `q` int64; rtol 1e-5, atol 1e-6 | 0 (exact). The statement warns that an int64 tensor × a Python float is float32 |
| `matrix-prefix-products-backward-pytorch` | float32; rtol 1e-4, atol 1e-5; own generator | 0.05 |

**Wave 4: iterative problems need a well-posed generator.** Two correct
implementations of an iteration agree only while it does not amplify rounding.
Gradient descent on an L-smooth convex loss is non-expansive for `lr < 2/L`,
so each GD generator caps `lr` by the worst case of its own draws, not by
the statement's bound:

- linear regression: `λ ≤ 2·max‖zᵢ‖²`;
- logistic and the ranker: `L ≤ ¼·max‖zᵢ‖²`;
- softmax: `L ≤ ½·max‖zᵢ‖²`;
- elastic net: `L ≤ max‖zᵢ‖² + α(1−ρ)`.

With features `|x| ≤ 1.5`–`2` and `d ≤ 10` that is `lr ≤ 0.04`–`0.19`.
Logistic regression drawn wide (features to 100, `lr` to 1, random labels, so
non-separable) disagreed by 5e6× tolerance. The large-margin traps live in the
stored cases, which the twins inherit.

`matrix-prefix-products-backward` draws `N ≤ 20` and `|W| ≤ 0.7` (the
statement allows `N ≤ 60` and `|W| ≤ 2`). A product of many random matrices
explodes or vanishes geometrically, and the statement promises entries below
1e6. Over 20,000 draws the largest entry was 2e4.
Wave 3 needed `$list` (ragged `Tensor[]` inputs, torch-runtime.md "Ragged lists") for GRPO and gradient clipping. Wave 2 needed dim expressions (`"D": "H*hd"`, `"H": "(Ho-1)*s + kh + r % s"`) and
`{"$dim": "H"}` for `numHeads` / `kernel` / `stride`. Two generators were cut
below the validator's sizes to fit the run's result budget (batch norm N ≤ 48,
d ≤ 24; attention backward n ≤ 32, d ≤ 16; sinusoidal 32 positions × d ≤ 64; and wave 1's layer norm, N ≤ 32,
D ≤ 48, whose old 64 × 64 draws could overflow it). The stored cases still
reach the full sizes.

`clip-loss-pytorch` (the torch-runtime pilot) is a PyTorch problem but **not a
twin**. It is forward-only, with `F` allowed, and has its own names and
constraints. `info-nce-contrastive-loss-pytorch` is the real twin of
`info-nce-contrastive-loss`.

## Status and next steps (2026-11-23)

**Done.** 33 twins in four waves: all of Tier A, and Tier B's wave 4.

- Wave 1 is `cac4e15` and wave 2 is `bd4199f`.
- Wave 3 (the ten twins from label-smoothed CE to KL/JS) and wave 4 (the nine
  from linear regression down) are `6a39878`; the `$list` ragged inputs they
  rely on are `fbeb601`.
- The starters' Args/Returns docstrings, numpy and twin alike, are `db7752c`.

Every twin is in `ml-coding-pytorch` and is tagged like its numpy problem plus
`pytorch`. Filters:

- `/?topic=pytorch` lists the PyTorch problems: the 33 twins and the
  `clip-loss-pytorch` pilot;
- `/?topic=machine-learning&exclude_topic=pytorch` lists the numpy ones.

Tooling built along the way:

- `scripts/sync_twin_tests.py` (`scaffold`, `statement`, `port`, `check`,
  `bake`) and `authoring/twins.py`;
- `tests/test_twins.py`;
- generator dim expressions and `{"$dim": …}`;
- `$list`, for ragged `Tensor[]` inputs;
- a structural input budget, `cost()`.

Each executor change had an `executor-security-reviewer` pass.

**float32 migration (2026-11-23).** 24 twins
moved from float64 to float32 (all but the 5 whose constraints need float64):
`tests/twin.json` (own generator + skips) in `authoring/twins.py`,
`sync_twin_tests.py port` and `tests/test_twins.py`; the shared numpy generators
lost their `"dtype": "float64"` pins; the batch-norm canonical differentiates the
explicit two-pass formula. Every float32 twin was cross-checked on its stored
cases plus 3000 draws, and hand-written correct solutions for layer norm, batch
norm, logistic regression and bilinear resize pass thousands of draws while the
typical wrong ones (one-pass variance, a naive sigmoid, a missing half-pixel
shift or clamp) fail.

**Next, in order:**

1. **Wave 5, ties.** Draw continuous values so that ties are
   improbable, and check what each statement promises about ties first. The
   problems:
   - `k-means-from-given-centroids`, `k-nearest-neighbors-classifier`,
     `non-maximum-suppression`;
   - `roc-auc`, `binary-classification-metrics`,
     `multiclass-precision-recall-f1`;
   - `moe-top-k-gating`, `top-k-top-p-sampling`;
   - `principal-component-analysis` (sign and order convention).
2. **Lower value, mostly indexing.** `pad-batch-and-attention-mask` (`$list` now
   covers its ragged input), `best-answer-span` and
   `speculative-decoding-acceptance`.
3. **Blocked on runtime work** (each change under `app/executor/` gets the
   `executor-security-reviewer`):
   - `$random` inside class-problem `{operations, args}` blocks `adam-optimizer`
     and `kv-cache-attention`;
   - walking `object` params blocks `gpt2-block-forward`;
   - nested `any[][][]` blocks `merge-partial-softmax-blocks`;
   - `matrix-factorization-gradient-descent` promises that no (user, item)
     pair appears twice in `ratings`, and a generator cannot draw distinct
     pairs. A per-item index inside `$list` (`u = k // items`, or a
     permutation) would be enough. Without one, random `randint` triples
     collide and the validator rejects them.
4. **Small extras.**
   - A generator cannot couple two parameters, so DPO random tests draw only
     `sigmoid`.
   - The list page has no "numpy only" toggle: `exclude_topic` works only from
     the URL.

Per twin, the steps are under "Adding a twin" above. Watch for these traps:

- one run's answers share a ~1 MB budget, so size the generator dims for the
  outputs;
- the harness calls the solver with keyword arguments, so hand-written test
  solutions must use the exact parameter names;
- scaffold leaves numpy wording it does not recognize, so grep the twin's
  statement for "numpy".

## Candidates still to do

Ranked by how much the PyTorch version is worth practising and how cleanly the
tests port. Notation: ⚠ = something to resolve when
authoring. Backward problems keep hand-written gradients, and shapes stay the
numpy ones.

### Tier A: done

All of Tier A has a twin (waves 1–3). The DPO generator draws only
`lossType = "sigmoid"`: `labelSmoothing` must be 0 for `"ipo"`, and a generator
cannot couple two parameters yet, so IPO is covered by the stored cases.

### Tier B: worth it, with a caveat

Wave 4 did nine of these. What is left:

| numpy problem | caveat |
|---|---|
| `matrix-factorization-gradient-descent` | iterative, so a float32-scale generator, as wave 4; blocked: `ratings` needs distinct (user, item) pairs, which a generator cannot draw |
| `adam-optimizer`, `kv-cache-attention` | class problems: `$random` inputs do not reach `{operations, args}` yet (torch-runtime "Not yet"), so `scaffold` refuses them |
| `gpt2-block-forward` | its `params` is an `object` holding matrices, which the input materializer does not walk |
| `merge-partial-softmax-blocks` | nested `any[][][]` input |
| `moe-top-k-gating`, `top-k-top-p-sampling` | `topk`/sort ties |
| `k-means-from-given-centroids`, `k-nearest-neighbors-classifier`, `non-maximum-suppression` | distance ties; integer outputs compare exactly |
| `roc-auc`, `binary-classification-metrics`, `multiclass-precision-recall-f1` | score ties |
| `principal-component-analysis` | eigenvector sign/order |
| `best-answer-span`, `speculative-decoding-acceptance`, `pad-batch-and-attention-mask` | mostly indexing; lower value |

### Tier C: no twin

- **The algorithm is the point:** `autograd-on-a-graph`.
- **Meaningless in float32:** `gradient-check-finite-differences`.
- **Small scalar math:** `symmetric-2x2-eigen`, `jacobi-gauss-seidel-solver`,
  `cosine-warmup-lr-schedule`.
- **Not tensor-shaped:** tokenizers, classical-ML counting models, RL tables,
  the streaming/sampling family, the LLM-systems simulations.

These can still get a `tests/generator.json` and baked random cases, without a
twin.
