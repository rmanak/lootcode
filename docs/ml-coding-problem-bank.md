# ML coding problem bank (research, 2026-10-30)

Companion to [`ml-coding-plan.md`](ml-coding-plan.md). This file is the **inventory**:
the ML coding problems I found that are reported from interviews or collected by
ML-interview prep sites, de-duplicated. Each one has a verdict on how it would fit
lootcode. Rows whose notes say **Shipped** are in the bank (69 problems as of
2026-10-31); [`ml-coding-todo.md`](ml-coding-todo.md) item 2 tracks what is left.

> **About the "Seen at" column.** These are company names that the cited source
> attaches to the problem. None of them is a company disclosure. They are
> candidate reports, vendor-curated "[V]" tags, or prep-list "historical
> preparation signals". Read them as *this shows up in loops like these*, not as a
> verified fact about one company. An empty cell means the source gives no company.

## Legend

**Pattern** is how the problem becomes a deterministic `input → expected` case.
The patterns are defined in [plan §3](ml-coding-plan.md#3-the-reframing):

| Code | Pattern | One-line rule |
|------|---------|---------------|
| **F**  | Pure function | Already deterministic (forward pass, metric, transform). Only needs the infra fixes. |
| **LG** | Loss & gradient | Your proposal: given params + data, return `[loss, grad]`. No training loop. |
| **PL** | Pinned loop | Keep the training loop, but pin init, learning rate, step count and update rule (they become inputs or are fixed in the statement). |
| **RI** | Randomness as input | Pass the random parts in: initial centroids, dropout mask, permutation, uniform draws. Never "seed + `np.random`". |
| **CL** | Class kind | Stateful (`fit`/`step`/`append`): an existing `kind: "class"` design problem with an operation sequence. |
| **TB** | Tie-break pinned | The statement fixes ties and sign conventions (argmax ties, eigenvector sign, equal distances). This tag is added on top of another pattern. |
| **CJ** | Custom judge | Only gradeable by a property (for example "loss ≤ optimum + ε"). Doesn't fit today. |
| **X**  | Out of scope | PyTorch-only, visual or notebook work, or not code. |

**Fit:** ✅ fits after the infra fixes in plan §2 · 🟡 fits, but the reframed version can't check the problem's real point · ❌ doesn't fit.

Source keys are listed under [Sources](#sources) at the bottom.

---

## A. Classical ML and optimization

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 1 | Pairwise ranking, logistic loss, linear scorer (RankNet-style) | your interview | OWN | LG + PL | ✅ | Worked example in [plan §3.3](ml-coding-plan.md#33-worked-example-your-ranking-problem). As asked, it has **no unique answer** (separable data, see plan G4). **Shipped** (2026-10-30) as `pairwise-ranker-i-loss-and-gradient` + `pairwise-ranker-ii-training`. |
| 2 | Linear regression by gradient descent | — | AIML, DML#15, YM2, TC#40 | PL / LG | ✅ | Deep-ML already pins `alpha` and `iterations` as inputs, which is the PL pattern. **Shipped** (2026-10-31) as `linear-regression-gradient-descent` (zero init, MSE history recorded before each step). |
| 3 | Linear regression, closed form (normal equation or least squares) | — | DML#14, YM2 | F | ✅ | Validator must guarantee full column rank and a sane condition number. Then `inv`, `solve` and `lstsq` all agree within tolerance. **Shipped** (2026-10-31) as `ridge-regression-closed-form` (`lam = 0` is the normal equation; unpenalized intercept). |
| 4 | Logistic regression by gradient descent (+ BCE loss history) | Google, Meta, Amazon (AIML); LinkedIn (BLI); Waymo phone screen, SentinelOne, Elastic, Neon (CM) | AIML, DML#106, YM2, CM | LG / PL | ✅ | The single most-cited classical problem. **Shipped** (2026-10-31) as `logistic-regression-gradient-descent` (zero init; loss recorded before each step). |
| 5 | Softmax (multinomial) regression by gradient descent | — | DML#105 | LG / PL | ✅ | **Shipped** (2026-10-31) as `softmax-regression-gradient-descent` (zero init; logits reach the thousands in a hidden test). |
| 6 | Ridge / Lasso / Elastic-net by gradient descent | — | DML#139 | PL | ✅ | Pin the L1 subgradient at exactly 0 (`sign(0) = 0`). **Shipped** (2026-10-31) as `elastic-net-gradient-descent` (subgradient, `sign(0) = 0`, sklearn-style objective). |
| 7 | Linear SVM, hinge loss (Pegasos) | LinkedIn (BLI) | AIML, DML#21 | LG / PL + RI | ✅ | Pin the subgradient at margin exactly 1. Pegasos's sample order is passed as an input. **Shipped** (2026-10-31) as `linear-svm-pegasos` (no bias, no projection; margin exactly 1 is not a violation). |
| 8 | Perceptron learning rule | — | AIML | PL | ✅ | Fixed pass order and epoch count. **Shipped** (2026-10-31) as `perceptron-learning-rule` (integer data, compare exact, stops after a clean epoch). |
| 9 | k-nearest neighbors (classify / regress) | Uber, LinkedIn, Meta (AIML) | AIML, YM2, DML#173 | F + TB | ✅ | Equal distances → lower index. Vote ties → smallest label. **Shipped** (2026-10-31) as `k-nearest-neighbors-classifier` (classification only). |
| 10 | k-means | Uber, LinkedIn, Google, Amazon (AIML); Meta (SUB); Google (DI); unnamed (BL1); Waymo and others (CM) | AIML, DML#17, YM2, CM | RI + PL + TB | ✅ | Initial centroids are an input (Deep-ML does exactly this). Pin max iterations, assignment ties and the empty-cluster rule. Most-reported problem overall. **Shipped** (2026-10-31) as `k-means-from-given-centroids`. |
| 11 | Decision-tree best split (Gini / information gain) | — | AIML, DML#138, DML#20 | F + TB | ✅ | Ties on gain → lowest feature, then lowest threshold. **Shipped** (2026-10-31) as `decision-tree-best-split` (Gini; gains within 1e-9 count as tied). |
| 12 | PCA | — | AIML, DML#19 | F + TB | ✅ | Pin the eigenvector sign (largest-magnitude entry positive). The validator ensures distinct eigenvalues. **Shipped** (2026-10-31) as `principal-component-analysis`. |
| 13 | Naive Bayes (multinomial text / Bernoulli) | — | AIML, DML#140 | F | ✅ | Pin the Laplace smoothing. Return log-probabilities or labels. **Shipped** (2026-10-31) as `multinomial-naive-bayes` (returns predictions and normalized log-posteriors). |
| 14 | Matrix factorization for recommendations (ALS / GD) | — | AIML | RI + PL | ✅ | Initial `U`, `V` are inputs. Use full-batch updates, or pass the SGD order in. **Shipped** (2026-10-31) as `matrix-factorization-gradient-descent` (full batch; the penalty covers unrated rows). |
| 15 | Gradient-boosting residual step / one AdaBoost round | — | AIML, DML#38 | F + TB | ✅ | **Shipped** (2026-10-31) as `adaboost-one-round` (decision stumps; gradient boosting not done). |

## B. Evaluation and data handling

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 16 | ROC-AUC + binary metrics (precision / recall / F1 at a threshold) | "ranking metrics from a classifier's scores and labels" (YM) | AIML, YM | F + TB | ✅ | Tied scores count ½. **Shipped** (2026-10-31) as `roc-auc` (AUC only; the threshold metrics are not in it). **Shipped** (2026-10-31) as `binary-classification-metrics` (the binary-metrics half; ROC-AUC shipped earlier). |
| 17 | Multiclass metrics, macro / micro averaging | — | AIML | F | ✅ | Pin 0/0 = 0. **Shipped** (2026-10-31) as `multiclass-precision-recall-f1` (per class, macro, weighted, micro). |
| 18 | Sample-weighted losses and streaming metrics | — | AIML | CL | ✅ | `update(batch)` / `result()`. **Shipped** (2026-10-31) as `streaming-weighted-metrics` (class kind: update / result / reset). |
| 19 | Train/val/test split without leakage; k-fold indices | — | AIML, DML#18 | F + RI | ✅ | The permutation is an input, or the split is deterministic by group. **Shipped** (2026-10-31) as `stratified-k-fold-indices` (the permutation is an input). |
| 20 | Standardize with training stats; missing values and unseen categories; one-hot | — | AIML, DML#16, DML#34 | F | ✅ | **Shipped** (2026-10-31) as `standard-scaler-and-one-hot`. |
| 21 | Uniform / weighted / stratified / reservoir sampling | — | AIML | RI | ✅ | The uniform draws are an input. The judge checks the draw → sample mapping. "Is it uniform?" can't be judged, and doesn't need to be. **Shipped** (2026-10-31) as `reservoir-sampling` (class kind) and `weighted-sampling-without-replacement` (Efraimidis–Spirakis keys). |
| 22 | Gradient check (finite differences) | "implement and debug backprop with a gradient check" (PH) | PH | F | ✅ | **Shipped** (2026-10-31) as `gradient-check-finite-differences` (central differences on a fixed logistic loss). |

## C. Neural-network building blocks

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 23 | Numerically stable softmax + cross-entropy (forward + gradient) | Apple, Meta, Google, Amazon (AIML); Amazon (SUB) | AIML, TC#2, TC#16, DML#134 | F / LG | ✅ | Hidden large-logit cases catch the naive `exp` version. Stability gets graded, which is the point of the question. **Shipped** (2026-10-31) as `softmax-cross-entropy-loss-and-gradient`. |
| 24 | Activations: stable sigmoid, ReLU, GELU, SwiGLU, SELU… | Amazon (SUB) | TC#1/15/19, DML#22/102/103/156 | F | ✅ | Pin GELU as exact-`erf` or the tanh approximation. `math.erf` needs no SciPy. **Shipped** (2026-10-31) as `gelu-and-stable-sigmoid` (sigmoid, its derivative, log-sigmoid, exact-erf GELU and its derivative). |
| 25 | Linear (dense) layer forward + backward | — | TC#3, DML#40 | LG | ✅ | Return `{"dX": …, "dW": …, "db": …}`. **Shipped** (2026-10-31) as `dense-layer-backward` (returns `[dX, dW, db]`; four activations). |
| 26 | MLP forward + backprop (2-layer) | unnamed (BL1, BL2); PH | AIML, DML#25, PH | LG / PL | ✅ | Weights are given and the answer is the gradients (LG). Or the initial weights are given with N steps (PL). **Shipped** (2026-10-31) as `two-layer-mlp-backprop` (ReLU + softmax CE, LG form). |
| 27 | LayerNorm / BatchNorm / RMSNorm / GroupNorm | — | TC#4/7/8, DML#109/115/126, YM | F (+ LG for backward) | ✅ | Pin `eps`, biased variance, and BatchNorm in training mode. **Shipped** (2026-10-31) as `layer-norm-forward-and-backward` (LayerNorm only; BatchNorm is wave D). **Shipped** (2026-10-31) as `batch-norm-training-forward-backward` (forward, full backward, PyTorch running statistics); LayerNorm shipped earlier. |
| 28 | Dropout | — | TC#17, DML#151 | RI | 🟡 | With the mask given, only the inverted-scaling detail is left to test. **Skipped** (2026-10-31): with the mask given, only the inverted scaling is left, which is too thin for a problem. |
| 29 | Conv2d (stride, padding) and pooling | prep guides ("2D convolution filter") | AIML, TC#22, DML#41/114 | F | ✅ | **Shipped** (2026-10-31) as `conv2d-stride-padding` and `max-pool-forward-backward` (first-maximum tie rule, overlapping windows accumulate). |
| 30 | Optimizers: momentum, Adam, AdaGrad, RMSProp, Nesterov | — | TC#29, DML#145–150 | CL / F | ✅ | `step(grad) → params`, or state in → state out. **Shipped** (2026-10-31) as `adam-optimizer` (class kind; Adam only). |
| 31 | LR schedules (step, cosine, warmup), gradient clipping, gradient accumulation | — | TC#21/30/31, DML#153–155 | F | ✅ | **Shipped** (2026-10-31) as `cosine-warmup-lr-schedule` and `gradient-clipping-by-global-norm` (overflow-safe norm). Gradient accumulation not built. |
| 32 | Weight init (Kaiming / Xavier) | — | TC#20 | RI | 🟡 | Random by nature. Only the computed std or bound can be graded. **Skipped** (2026-10-31): only a computed std or bound can be graded, a one-line formula. |
| 33 | Embedding lookup; pad variable-length batches + attention mask | — | TC#18, AIML (LM) | F | ✅ | **Shipped** (2026-10-31) as `pad-batch-and-attention-mask` (ids, mask, position ids, causal mask; padId may be a real token). Embedding lookup not built. |
| 34 | Autograd engine (micrograd-style) | OpenAI (PH); "frontier labs" (YM) | DML#26, PH, YM | F (reframed) | 🟡 | Reframing: the expression graph comes as a JSON node list, and the answer is the forward value plus every node's gradient. This keeps the backward-pass logic (topological order, gradient accumulation) but loses the operator-overloading API design. **Shipped** (2026-10-31) as `autograd-on-a-graph` (JSON node list in any order; forward value plus every node's gradient; relu′(0) = 0). |
| 35 | INT8 quantization (scale, zero point, clipping) | NVIDIA (PH) | TC#36, PH | F + TB | ✅ | Pin the rounding mode. `np.round` rounds half to even. **Shipped** (2026-10-31) as `int8-affine-quantization` (calibrate, quantize with half-to-even rounding and clipping, dequantize). |
| 36 | Debug a broken training / inference loop | "frontier labs" (YM) | YM | F / PL | ✅ | The **starter code is the buggy implementation**, so it fits the editor model unchanged. **Shipped** (2026-10-31) as `debug-broken-training-loop` (mini-batch logistic regression with seven planted bugs). |

## D. Transformers and LLMs

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 37 | Scaled dot-product attention (+ mask) | Meta (PH); Amazon (SUB) | AIML (LM), TC#5, PH | F | ✅ |**Shipped** (2026-10-31) as `scaled-dot-product-attention` (returns output and weights). |
| 38 | Multi-head / causal self-attention (weights as inputs) | Meta (SUB); Amazon, ByteDance ×2 (PH) | TC#6/9, DML#107, PH | F | ✅ |**Shipped** (2026-10-31) as `multi-head-causal-self-attention`. |
| 39 | GQA / sliding-window / linear / cross attention | — | TC#10–12/23, DML#131 | F | ✅ | **Shipped** (2026-10-31) as `grouped-query-attention` (GQA; MHA and MQA as the two extremes). Sliding-window, linear and cross attention not built. |
| 40 | KV cache | Anthropic, OpenAI, Meta, Perplexity (AIML); "frontier labs" (YM) | AIML (LM), TC#14 | CL | ✅ | `append(k, v)` / `attend(q)` is a natural design problem. **Shipped** (2026-10-31) as `kv-cache-attention`, with a sliding window (`maxLen`) added so the class has real state. |
| 41 | Positional encodings: sinusoidal, RoPE | — | AIML (LM), TC#24 | F | ✅ | **Shipped** (2026-10-31) as `sinusoidal-positional-encoding` (odd d allowed) and `rotary-position-embedding` (both pair layouts, positions as input). |
| 42 | Temperature / top-k / top-p sampling | Anthropic, OpenAI, DeepMind (AIML) | AIML (LM), TC#32 | F / RI | ✅ | Return the filtered, renormalized distribution (F), or take a uniform `u` and return the token (RI). **Shipped** (2026-10-31) as `top-k-top-p-sampling` (returns the token and the final distribution). |
| 43 | Greedy and beam-search decoding | Microsoft (PH); "frontier labs" (YM) | TC#33, PH | F + TB | ✅ | The "model" is a lookup table (bigram log-prob matrix). Pin ties and length handling. **Shipped** (2026-10-31) as `beam-search-decoding` (beam search; no length normalization). |
| 44 | BPE tokenizer: learn merges + encode | — | AIML (LM), TC#35 | F + TB | ✅ | Pure strings. **Needs no numpy, so it fits today.** **Shipped** (2026-10-31) as `bpe-tokenizer`. |
| 45 | TF-IDF; cosine-similarity top-k retrieval (RAG) | Apple, cosine (SUB); Harvey, retrieval (PH) | AIML (LM, GenAI), PH | F + TB | ✅ | Pin tokenization, the log base and smoothing. **Shipped** (2026-10-31) as `tf-idf-cosine-retrieval` (sklearn smooth idf, top-k with index tie-break, scores returned). |
| 46 | LoRA forward / merge | Meta, Google, Anthropic, OpenAI, Databricks (AIML); YM | AIML (GenAI), TC#26 | F | ✅ | **Shipped** (2026-10-31) as `lora-forward-and-merge` (alpha/r and rsLoRA scaling). |
| 47 | Contrastive (CLIP / InfoNCE) loss | OpenAI, Anthropic, DeepMind, Midjourney (AIML) | AIML (GenAI) | F / LG | ✅ | **Shipped** (2026-10-31) as `info-nce-contrastive-loss` (symmetric CLIP loss plus gradients through the L2 normalization). |
| 48 | DPO / PPO / GRPO losses (given log-probs) | Anthropic, OpenAI, DeepMind, Meta (AIML) | AIML (GenAI), TC#37–39, DML#101 | F | ✅ | A formula over given arrays, so a very clean fit. **Shipped** (2026-10-31) as `dpo-loss` (sigmoid, cDPO label smoothing, IPO; implicit rewards and accuracy) and `grpo-clipped-objective` (group advantages, PPO clip, k3 KL, two aggregations). |
| 49 | Mixture-of-experts top-k (noisy) gating | — | TC#28, DML#124/125 | F / RI | ✅ | The noise is an input. **Shipped** (2026-10-31) as `moe-top-k-gating` (Mixtral softmax over the top k, token-order capacity with dropping, Switch aux loss). No noise term: the noise would just be an added input matrix. |
| 50 | Speculative-decoding acceptance | — | TC#34 | RI | ✅ | The uniform draws are inputs. The accept/resample rule is deterministic. **Shipped** (2026-10-31) as `speculative-decoding-acceptance` (accept/reject, residual resample, bonus token; exact compare). |
| 51 | Classifier-free guidance | — | AIML (GenAI) | F | ✅ | **Shipped** (2026-10-31) as `classifier-free-guidance` (stacked [uncond; cond] batch, diffusers guidance rescale). |
| 52 | Flash attention (tiled, online softmax) | — | TC#25 | F | 🟡 | The output equals plain attention, so the judge can't see whether tiling was used. A checkable alternative: "merge two partial softmax blocks". **Shipped** (2026-10-31) as `merge-partial-softmax-blocks` (merge [m, l, o] block summaries into [M, L, LSE, O]; masked blocks as null). |
| 53 | GPT-2 block forward | — | TC#13 | F | ✅ | Keep dimensions tiny (d ≤ 16) so the weights fit in JSON. **Shipped** (2026-10-31) as `gpt2-block-forward` (pre-LN, fused QKV, tanh GELU; params as one object). |

## E. Vision

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 54 | IoU + non-maximum suppression | unnamed (BL1) | BL1, RF | F + TB | ✅ | Pin the box format, score ties, and a strict `>` threshold. **Shipped** (2026-10-31) as `non-maximum-suppression`. |
| 55 | Implement an unfamiliar image/signal formula (blur, scaling) from its definition | Apple (SUB) | SUB | F | ✅ | **Shipped** (2026-10-31) as `bilinear-image-resize` (PyTorch `F.interpolate` semantics, both `align_corners` modes, the negative-source clamp). |

## F. Reinforcement learning (from Deep-ML; rarely reported in interviews)

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 56 | Value iteration / policy evaluation / Bellman update | — | DML#142/157 | F | ✅ | **Shipped** (2026-10-31) as `value-iteration` (synchronous sweeps, stop rule, sweep count, lowest-index greedy policy). |
| 57 | Q-learning, ε-greedy, REINFORCE | — | DML#122/133/158 | RI | ✅ | The episodes or draws are inputs. **Shipped** (2026-10-31) as `q-learning-updates` (Q-learning, SARSA, expected SARSA under ε-greedy, from recorded episodes). REINFORCE not built. |

## G. Agentic AI coding (plain Python, no numpy)

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 58 | Validate tool args; permission-aware tool registry; retry with idempotency; sliding-window conversation memory; bounded tool-use loop | — | AIML (Agentic) | F / CL | ✅ | **Fits today with no infra change.** These are ordinary function and design problems. **Shipped** (2026-10-31) as `validate-tool-call-arguments` (JSON-Schema subset, strict parse, ordered error paths), `conversation-memory-window` (CL; token budget, atomic tool groups, placeholder) and `idempotency-key-retries` (CL; replay, conflict, cached declines, injected failures, TTL). Permission-aware registry and bounded tool loop not built. |

## H. Linear-algebra drills

| # | Problem | Seen at | Sources | Pattern | Fit | Notes |
|---|---------|---------|---------|---------|-----|-------|
| 59 | Covariance / correlation, Jacobi solver, SVD/eigen of 2×2, determinant… | — | DML#1–13/27/28/35/37 | F | ✅ | Low interview value, since most are numpy one-liners. Take a handful at most. **Shipped** (2026-10-31) as `covariance-and-correlation` (ddof, constant columns, a large-offset stability case), `jacobi-gauss-seidel-solver` and `symmetric-2x2-eigen` (stable eigenvalues, sign convention). |

## I. Doesn't fit

| # | Problem | Seen at | Sources | Pattern | Fit | Why |
|---|---------|---------|---------|---------|-----|-----|
| 60 | "Train a model on this data", with free choice of optimizer and stopping, or hit ≥ X accuracy | "build a model and train it / overfit toy samples" (YM) | YM, CM | CJ | ❌ | The answer depends on the solver's choices. It needs a property judge: accept if `L(w) ≤ L* + ε` or held-out accuracy ≥ a threshold. The PL variant (#1, #2, #4) is the fitting substitute. |
| 61 | PyTorch-specific: write a PyTorch training loop, a custom `autograd.Function`, "gradients flow" checks | Amazon (SUB); OpenAI autograd on torch tensors (PH) | SUB, PH, TC | X | ❌ | Torch in the sandbox, see [plan §2](ml-coding-plan.md#2-does-it-fit-lootcodes-framework-today). Most *torch-phrased* problems (attention, norms, LoRA) translate to numpy without loss and are already in rows above. |
| 62 | Notebook / EDA / visual exercises; "explain the math", production and scale follow-ups | — | AIML (notebook items), CM | X | ❌ | There is no code output to grade. |

---

## Tally

| Verdict | Count | Rows |
|---------|------:|------|
| ✅ fits after infra fixes | 55 | everything not listed below |
| 🟡 fits, but the reframing can't check the problem's real point | 4 | 28 dropout, 32 init, 34 autograd, 52 flash attention |
| ❌ doesn't fit (needs a custom judge or torch, or isn't code) | 3 | 60, 61, 62 |
| **Total** | **62** | |

How the 55 ✅ rows become deterministic (the dominant pattern per row):

| Pattern | Rows | Share of ✅ |
|---------|-----:|-----:|
| F, pure function (infra only) | 36 | 65% |
| LG / PL, your loss-and-gradient idea or the pinned loop | 9 | 16% |
| RI, randomness as input | 6 | 11% |
| CL, class kind | 4 | 7% |

Several F rows (23 softmax+CE, 27 norms, 47 contrastive loss) also have a natural
LG variant ("…and its gradient"). So your loss-and-gradient idea is the right tool
for about a quarter of the bank, not only the 9 rows where it is the main pattern.

---

## Sources

| Key | Source | What it gives |
|-----|--------|---------------|
| OWN | `ml_problems.txt` (repo root) | The pairwise-ranking problem from your interview. |
| AIML | [alirezadir/AIMLInterviews: ML coding](https://github.com/alirezadir/Machine-Learning-Interviews/blob/main/src/MLC/ml-coding.md) | 41 problems in four groups (classic ML, LM, GenAI, agentic), with company tags. |
| DML | [Deep-ML open problem bank (Open-Deep-ML/DML-OpenProblem)](https://github.com/Open-Deep-ML/DML-OpenProblem) · [deep-ml.com](https://www.deep-ml.com/problems) | 100+ numpy problems, judged LeetCode-style. Their [lin-reg GD tests](https://raw.githubusercontent.com/Open-Deep-ML/DML-OpenProblem/main/questions/15_linear-regression-using-gradient-descent/tests.json) pin `alpha`/`iterations` and compare **outputs rounded to 4 decimals**. Their k-means takes `initial_centroids` as an input. License is "educational use only", so **write our own statements; don't copy theirs**. |
| TC | [TorchCode README](https://huggingface.co/spaces/duoan/TorchCode/blob/main/README.md) | 41 PyTorch problems with interview-frequency ratings. Judged with `torch.allclose` and gradient-flow checks. |
| PH | [PracHub ML coding questions](https://prachub.com/positions/software-engineer/categories/machine-learning) · [scaled dot-product attention](https://prachub.com/coding-questions/implement-scaled-dot-product-attention) · [MHA in numpy](https://prachub.com/coding-questions/implement-multi-head-attention-from-scratch-in-numpy) | Company-attributed questions: OpenAI, ByteDance, NVIDIA, Harvey, Meta, Amazon, Microsoft. Partly paywalled. |
| SUB | [AI Engineering Insider: 105+ MAANG AI engineer questions](https://aiengineeringinsider.substack.com/p/105-maang-ai-engineer-interview-questions) | Meta / Amazon "[V]" and Apple "[R]" coding items. |
| YM | [Yuan Meng: MLE Interview 2.0](https://www.yuan-meng.com/posts/mle_interviews_2.0/) | Frontier-lab "LLM coding" rounds (transformer, LoRA, KV cache, beam search, autograd, debugging), plus classic from-scratch rounds. |
| YM2 | [Yuan Meng: Code ML algorithms from scratch](https://www.yuan-meng.com/posts/md_coding/) | "The 4 commonly asked": linear reg, logistic reg, kNN, k-means. |
| BL1 | [Blind: DoorDash ML coding round](https://www.teamblind.com/post/doordash-ml-coding-round-gz7deqot) | One reply reports doing k-means, NMS and an MLP in interviews, "generally numpy allowed". |
| BL2 | [Blind: coding MLP from scratch with numpy](https://www.teamblind.com/post/coding-mlp-from-scratch-using-numpy-and-python-cr2npxpb) | MLP + backprop from scratch. |
| BLI | [Blind: LinkedIn data coding interview](https://www.teamblind.com/post/linkedin-data-coding-interview-3deyd0vw) | Logistic regression or SVM from scratch. |
| DI | [DataInterview: data scientist coding interview](https://datainterview.com/blog/data-scientist-coding-interview) | Google: k-means with only NumPy. |
| CM | [Codemia: k-means from scratch](https://codemia.io/practice/implement-k-means-from-scratch-16) · [logistic regression from scratch](https://codemia.io/practice/implement-logistic-regression-from-scratch-8) | Stage and company listings (Waymo phone screen, SentinelOne onsite, Elastic take-home, Neon). Titles and descriptions sometimes mismatch. |
| RF | [Roboflow: NMS in plain NumPy](https://blog.roboflow.com/how-to-code-non-maximum-suppression-nms-in-plain-numpy/) | Tutorial, not an interview report. Used as the IoU/NMS reference. |
| — | [Tensor-Puzzles (srush)](https://github.com/srush/Tensor-Puzzles) · [Pyre Code](https://gittrend.io/repo/whwangovo/pyre-code) | Other judged practice sets: 21 broadcasting puzzles; 68 self-hosted ML problems. Not mined row by row. |
