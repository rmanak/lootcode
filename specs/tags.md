# Problem tag taxonomy

lootcode tags every problem from a **fixed canonical vocabulary** so the
browse/filter facets stay meaningful and near-synonyms don't multiply.

- **Authoritative source:** `app/tags.py` — `CANONICAL_TAGS`, `TAG_ALIASES`,
  `DROPPED_TAGS`, and `normalize_tags()`. This doc is prose; the code is law.
- **Authoring workflow:** the `canonical-tags` skill (`.claude/skills/canonical-tags/`).
- **Enforcement:** `app.content.write_problem_files` runs `normalize_tags` on
  every write (manual admin, AI generator, bulk-import generators), so aliases
  are corrected, dropped tags removed, and no problem is ever left tagless.

## Canonical tags (62)

| Group | Tags |
|---|---|
| Core data shapes | `array`, `string`, `matrix`, `linked-list`, `tree`, `binary-tree`, `graph` |
| Structures | `stack`, `monotonic-stack`, `queue`, `heap`, `hash-table`, `hash-function`, `binary-search-tree`, `ordered-set`, `trie`, `union-find`, `binary-indexed-tree`, `segment-tree`, `suffix-array`, `design` |
| Techniques | `two-pointers`, `sliding-window`, `prefix-sum`, `binary-search`, `sorting`, `greedy`, `backtracking`, `recursion`, `divide-and-conquer`, `dynamic-programming`, `memoization`, `depth-first-search`, `breadth-first-search`, `topological-sort`, `shortest-path`, `bit-manipulation`, `bitmask` |
| Counting / numeric | `combinatorics`, `counting`, `simulation`, `number-theory`, `geometry`, `math` |
| Domain | `machine-learning` |
| ML topics (only with `machine-learning`) | `loss-function`, `backpropagation`, `optimization`, `classical-ml`, `neural-networks`, `transformer`, `decoding`, `llm-inference`, `llm-apps`, `reinforcement-learning`, `evaluation-metrics`, `statistics`, `data-preprocessing`, `nlp`, `computer-vision`, `linear-algebra` |
| ML framework (only with `machine-learning`) | `pytorch` |

`design` tags problems that ask you to **implement a data structure** driven by a
sequence of operations (the input is an operations list, e.g.
`["LRUCache", "put", "get", ...]` with per-op arguments; the harness
support this shape). Use it for the "build/design a structure" pattern, not for
one-shot computational problems.

`machine-learning` tags **ML coding** problems: losses and their gradients, training
loops, metrics, model building blocks (attention, normalization, sampling), the
"implement it from scratch with numpy" interview round. It names the *domain*;
every such problem is also listed in the `ml-coding` collection.

Next to it, every ML problem carries **1–3 ML topic tags** saying what it
practises (`app/tags.py::ML_TOPIC_TAGS`). They never appear without
`machine-learning`, and `tests/test_tags.py` checks both rules over the bank:

| Tag | What it covers |
|---|---|
| `loss-function` | Cross-entropy, contrastive, preference and divergence losses |
| `backpropagation` | Backward passes, autograd, gradient checking |
| `optimization` | Optimizers, LR schedules, gradient clipping, gradient-descent training loops |
| `classical-ml` | Pre-deep-learning models: linear/logistic/softmax regression, SVM, perceptron, naive Bayes, trees, ensembles, kNN, k-means, PCA |
| `neural-networks` | Layers, activations, normalization, conv/pool, LoRA, MoE |
| `transformer` | Attention variants, positional encodings, transformer blocks |
| `decoding` | Turning model scores into outputs: beam search, top-k/top-p sampling, speculative decoding, span extraction, guidance |
| `llm-inference` | Serving: batching, KV/prefix caches, quantization, speculative decoding, graph compilation |
| `llm-apps` | RAG, agents, tool calls, context and memory management |
| `reinforcement-learning` | MDPs, Q-learning, bandits, policy and preference objectives |
| `evaluation-metrics` | Classification metrics, ROC-AUC, cross-validation, confidence intervals |
| `statistics` | Moments, sampling, resampling, entropy |
| `data-preprocessing` | Scaling and encoding, batching and padding, data-mixing loaders, label cleaning |
| `nlp` | Tokenizers, text models, text retrieval |
| `computer-vision` | Image ops, detection, 3-D fitting, image–text and diffusion |
| `linear-algebra` | Eigen-decomposition, iterative solvers, closed forms, factorization |

Pick the topic the problem *practises*, not every one it touches: a model fitted by
gradient descent is `classical-ml` + `optimization`; a fused forward/backward layer
is `neural-networks` + `backpropagation`. Add a general technique tag only when the
problem is genuinely about one too (`heap` for a top-k retrieval, `design` for a
KV cache). `statistics` and `linear-algebra` are ML topics, not general math tags:
a non-ML probability or matrix problem stays `math` / `matrix`.

`pytorch` is the one **framework** tag (`app/tags.py::ML_FRAMEWORK_TAGS`). It
says which library the problem is solved in, not what it practises, so it does
not count toward the 1–3 topic tags. A problem carries it **exactly** when it
runs on the PyTorch runtime (`"runtime": "torch"`, `docs/torch-runtime.md`), and
`tests/test_tags.py` pins that both ways. An ML problem without it is a numpy
problem. Most PyTorch problems are deliberate twins of a numpy one
(`docs/pytorch-twins.md`) and sit in the `ml-coding-pytorch` collection.

`math` is a **catch-all umbrella**: kept only when no more specific canonical tag
applies (arithmetic-formula and probability problems), and used as the fallback so
a problem is never tagless. When a specific tag is present — including the two
that were split out of it, `number-theory` and `geometry` — the redundant `math`
is stripped.

Three more pairs are deliberately kept **apart** rather than folded together:
`binary-indexed-tree` vs `segment-tree` (different structures), `binary-search-tree`
vs `ordered-set` (a BST as the problem's subject vs a sorted container used as a
tool), and `graph` vs its two named techniques `topological-sort` and
`shortest-path`.

## Aliases (non-canonical → canonical)

Synonyms/abbreviations and too-detailed techniques fold up into a broader kept
category. Full map in `app/tags.py:TAG_ALIASES`:

- `bfs` → `breadth-first-search`; `dfs`, `flood-fill` → `depth-first-search`
- `hashing`, `hash-set` → `hash-table`
- `bucket-sort`, `counting-sort`, `radix-sort`, `quickselect`, `merge-sort`,
  `interval`, `intervals`, `sweep-line`, `line-sweep` → `sorting`
- `monotonic-queue` → `queue`; `heap-priority-queue`, `priority-queue` → `heap`
- `doubly-linked-list` → `linked-list`
- `data-stream`, `iterator` → `design`
- `interval-dp`, `game-theory` → `dynamic-programming`
- `string-matching`, `rolling-hash` → `string`
- `biconnected-component`, `bridges`, `eulerian-path`, `eulerian-circuit`,
  `minimum-spanning-tree` → `graph`; `dijkstra` → `shortest-path`
- `probability`, `probability-and-statistics` → `math`
- `ml`, `deep-learning`, `neural-network` → `machine-learning`
- `torch` → `pytorch`

## Dropped (removed entirely)

Too vague or a problem-type meta-tag with no good home: `enumeration`, `queries`,
`brainteaser`. Also dropped are tags that describe how a problem is *delivered*
rather than how it is solved — `database`, `shell` and `concurrency` name a
language we don't run, and `interactive`, `randomized` and `reservoir-sampling`
name a judging style we re-author away. Never use these.

## Extending the vocabulary

Don't invent tags inline. If a problem genuinely fits none of the canonical
tags, discuss with the owner first; if agreed, add the tag to `CANONICAL_TAGS`
in `app/tags.py`, document it here, and refresh the `canonical-tags` skill list.
