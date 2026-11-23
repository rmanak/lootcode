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
| stored tests | hand-curated + baked `gen-*` cases with `expected` | every numpy case, same name, weight and hidden flag, `expected: null`; plus optional twin-only `torch-*` cases |
| random tests | baked from `tests/generator.json` | drawn from the same generator on **every run** |
| inputs | plain lists | numeric arrays become tensors (`int`/`bool` arrays as int64/bool); scalars and strings stay plain values |
| return | lists and numbers | the same structure, tensors in place of arrays, 0-dim tensors in place of numbers |
| hand-written gradients | yes (numpy has no autograd) | **still hand-written**: `torch.forbid` lists the autograd entry points |
| the built-in that *is* the exercise | n/a | forbidden (`F.cross_entropy` in the cross-entropy problem, `F.layer_norm` in layer norm, …) |
| judging | `close`: rel 1e-6 / abs 1e-9 | allclose `rtol=1e-5`, `atol=1e-6`; shape and dtype exact |

**dtype.** A twin is float32 unless float32 cannot meet the tolerance on the
numpy problem's constraints, and then it is float64. Most numpy ML problems
deliberately include ill-conditioned traps that are fine in float64 and
hopeless in float32:

- logits near ±1000 at τ = 0.001;
- rows with mean 1000 and spread 0.001;
- scores in the tens of thousands;
- `1 − tanh²` at saturation.

Two correct float32 solutions disagree with each other there. The constraints
stay the numpy ones, so the twin's dtype moves instead. A float64 twin is also
closer to the original, which computes in float64 too. The dtype is pinned in
the shared generator (`"dtype": "float64"` on the tensor specs), which the numpy
side ignores. `port` then wraps the twin's literal inputs as float64. The
statement and the page say which dtype arrives.

**What the twin forbids** is decided per problem by one rule: forbid what the
statement asks you to implement, and nothing else. Indexing, broadcasting,
`masked_fill`, `torch.erf`, `torch.softmax` (when the softmax is not the point)
and `torch.log1p` stay allowed, because using them well is the PyTorch skill
being practised.

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
  the twin's canonical with **autograd and the library built-ins** (it is never
  forbidden anything): it is then independent of the numpy canonical's
  hand-derived math, so agreement is real evidence that both are right.

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
# 3. Scaffold the twin (--autograd-forbidden for a hand-written-gradient problem).
.venv/bin/python $S scaffold <slug> --autograd-forbidden --write
#    Then by hand:
#    - solution/solution.py: the reference, using autograd/built-ins freely;
#    - meta.json torch.forbid: add the built-in that IS the exercise, its
#      neighbours that do the same job (F.layer_norm on x.T is a batch norm)
#      and their torch.ops.aten kernels (private ones too: _log_softmax);
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
#      After any meta edit (forbid, return type, dtypes) refresh the generated
#      paragraphs; --out-dtype when integer inputs give a float answer:
.venv/bin/python $S statement <slug> [--out-dtype float64] --write
# 4. Copy the tests across and cross-check.
.venv/bin/python $S port <slug> --write
.venv/bin/python $S check <slug>       # fails? usually float32: pin float64 in the
                                       # generator, port, re-check
# 5. Hand-written solutions: one correct one passes, and the typical wrong ones
#    and the forbidden built-ins fail. Then `make check`.
```

**When the numpy problem changes** (new cases, a re-bake, a generator edit),
run `port <slug> --write`. `tests/test_twins.py` fails until you do. It pins:

- the contract;
- the byte-identical validator;
- the tags;
- the shared generator;
- the ported cases;
- the forbid names;
- the collection order.

## The twins

| twin | dtype | forbidden | cross-check (× tolerance) |
|---|---|---|---|
| `info-nce-contrastive-loss-pytorch` | float64 | autograd | 6e-8 (float32 was 5×, at τ = 0.001) |
| `softmax-cross-entropy-loss-and-gradient-pytorch` | float32 | autograd, `cross_entropy`, `nll_loss`, `log_softmax`, `logsumexp` | 0.017 |
| `scaled-dot-product-attention-pytorch` | float64 | `F.scaled_dot_product_attention` | 2e-6 (float32 was 596×) |
| `layer-norm-forward-and-backward-pytorch` | float64 | autograd, `layer_norm`, `group_norm` | 7e-6 (float32 was 1.5e5×). The reference differentiates the explicit two-pass formula: `F.layer_norm`'s fused backward returned -4e-7 for an exact 0 (a constant row, eps = 1e-12), 0.42× tolerance on its own |
| `gelu-and-stable-sigmoid-pytorch` | float32 | autograd, `gelu`, `sigmoid`, `logsigmoid`, `ndtr` | 0.25 |
| `dense-layer-backward-pytorch` | float64 | autograd | 5e-8 (float32 was 7×: `1 − tanh²`) |
| `sinusoidal-positional-encoding-pytorch` | int64 positions in, float64 out | — | 1e-5 (positions up to 1e5: float32 angles are off by ~4e-3) |
| `rotary-position-embedding-pytorch` | float64 | — | 3e-5 |
| `multi-head-causal-self-attention-pytorch` | float64 | `F.scaled_dot_product_attention`, `F.multi_head_attention_forward` | 4e-6 |
| `grouped-query-attention-pytorch` | float64 | the same | 8e-7 |
| `distance-decay-attention-pytorch` | float64 | the same | 8e-8 |
| `attention-backward-pass-pytorch` | float64 | autograd, the same, `_softmax_backward_data` | 4e-6 |
| `batch-norm-training-forward-backward-pytorch` | float64 | autograd, `batch_norm`, and `instance_norm` / `layer_norm` / `group_norm` (each does a batch norm on a reshaped input) | 5e-6 |
| `max-pool-forward-backward-pytorch` | float32 (`x` on integers, `dout` on a 1/16 grid, so sums are exact) | autograd, `max_pool1d/2d/3d`, `adaptive_max_pool2d`, `max_unpool2d` | 0.12 (a stored case with arbitrary decimals) |
| `label-smoothed-masked-cross-entropy-pytorch` | float32 | autograd, `cross_entropy`, `nll_loss`, `log_softmax`, `logsumexp` | 0.039 |
| `dpo-loss-pytorch` | float64 | autograd, `logsigmoid`, `softplus`, `binary_cross_entropy_with_logits` (`torch.logaddexp` stays allowed: numpy has it) | 3e-11 |
| `grpo-clipped-objective-pytorch` | float64; the three log-prob lists are `Tensor[]` (one tensor per completion, `$list` with `share`) | — | 1e-10 |
| `conv2d-stride-padding-pytorch` | float64; `weight` is `Tensor` (numpy types the 4-D weight `any[]`) | `conv1d/2d/3d`, `conv_transpose2d`, `torch.convolution` and the aten convolution kernels (`nn.Conv2d` raises too: it calls `F.conv2d`). `F.unfold` stays allowed | 2e-8 |
| `two-layer-mlp-backprop-pytorch` | float64 | autograd | 2e-8 |
| `lora-forward-and-merge-pytorch` | float64 | — | 3e-8 |
| `classifier-free-guidance-pytorch` | float64 | — (`torch.std`'s unbiased default matches, and the rescale ratio cancels it anyway) | 5e-9 |
| `gradient-clipping-by-global-norm-pytorch` | float64; `grads` is `Tensor[]` (`$list`) | `clip_grad_norm_` and friends. `torch.linalg.vector_norm` returns `inf` on the 1e200 entries, so the overflow trap survives | 5e-11 |
| `pairwise-ranker-i-loss-and-gradient-pytorch` | float64 | autograd, as DPO | 1e-4 |
| `kl-and-js-divergence-pytorch` | float64 | `kl_div`, `kl_divergence` | 1e-10. The generator draws all-positive weights (no shared zero pattern); the stored cases cover zeros |
| `linear-regression-gradient-descent-pytorch` | float64 | autograd | 2e-8 |
| `logistic-regression-gradient-descent-pytorch` | float64 | autograd, as DPO (the stable log-loss is part of the exercise) | 2e-10 (a wide generator was 5e6×: chaotic, see below) |
| `softmax-regression-gradient-descent-pytorch` | float64 | autograd, as softmax CE | 2e-10 |
| `elastic-net-gradient-descent-pytorch` | float64 | autograd (autograd's `abs` gradient at 0 is 0, the statement's `sign(0)`) | 1e-9. Over 2,000 draws the smallest nonzero weight `sign` read was 1.2e-6, so the "never within 1e-9 of 0" promise holds |
| `pairwise-ranker-ii-training-pytorch` | float64 | autograd (no loss is returned, so the loss built-ins stay allowed) | 5e-11 |
| `bilinear-image-resize-pytorch` | float64 | `interpolate`, `upsample`, `upsample_bilinear`, `grid_sample`, `grid_sampler(_2d)` | 1e-8 (float32 was 7×: `F.interpolate` computes source coordinates in float32, and pixels reach 255) |
| `covariance-and-correlation-pytorch` | float64 | `torch.cov`, `torch.corrcoef` | 2e-7. The generator draws a per-test offset up to 1e8 with spread down to 0.5, so the one-pass-variance trap comes up live |
| `int8-affine-quantization-pytorch` | float64 in; `zeroPoint` and `q` int64 | `quantize_per_tensor(_dynamic)`, `fake_quantize_per_tensor_affine`, the learnable fake-quant, and the observers' shared `UniformQuantizationObserverBase._calculate_qparams` | 0 (exact). The statement warns that an int64 tensor × a Python float is float32 |
| `matrix-prefix-products-backward-pytorch` | float64 | autograd | 3e-10 |

Every forbid list also names the `torch.ops.aten` kernels behind its built-ins.

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
- `torch.forbid`;
- generator dim expressions and `{"$dim": …}`;
- `$list`, for ragged `Tensor[]` inputs;
- a structural input budget, `cost()`.

Each executor change had an `executor-security-reviewer` pass.

**Next, in order:**

1. **Wave 5, ties.** Draw continuous float64 values so that ties are
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
tests port. Notation: **F** = forbid list, ⚠ = something to resolve when
authoring. Backward problems keep hand-written gradients (autograd forbidden),
and shapes stay the numpy ones.

### Tier A: done

All of Tier A has a twin (waves 1–3). The DPO generator draws only
`lossType = "sigmoid"`: `labelSmoothing` must be 0 for `"ipo"`, and a generator
cannot couple two parameters yet, so IPO is covered by the stored cases.

### Tier B: worth it, with a caveat

Wave 4 did nine of these. What is left:

| numpy problem | caveat |
|---|---|
| `matrix-factorization-gradient-descent` | iterative, so float64 and autograd forbidden, as wave 4; blocked: `ratings` needs distinct (user, item) pairs, which a generator cannot draw |
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
