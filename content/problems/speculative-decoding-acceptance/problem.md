# Speculative Decoding: Accept, Reject, Resample

Generating with a big model is slow because it produces one token per forward
pass. **Speculative decoding** lets a small *draft* model guess $k$ tokens
ahead. The big *target* model then scores all of them in a single pass. A
clever accept/reject rule keeps the output distributed **exactly** as if the
target model had sampled every token itself. Implement one speculative step.

**Inputs.** `draftTokens` holds the $k$ tokens the draft model sampled.
`draftProbs[i]` is the draft model's distribution over the vocabulary at
position $i$, the one `draftTokens[i]` was drawn from. `targetProbs` has
$k + 1$ rows: the target model's distribution at each of the $k$ draft
positions, plus one more after the last draft token. The randomness comes in
as inputs, so the result is deterministic: `u[i]` is a uniform number for
position $i$, and `uSample` is one more uniform number for the final sampling
step.

**The step.** For $i = 0, 1, \dots, k - 1$, with $x$ = `draftTokens[i]`,
$p$ = `targetProbs[i][x]` and $q$ = `draftProbs[i][x]`:

- **Accept** $x$ if `u[i]` $< p / q$ (strictly), so with probability
  $\min(1, p / q)$. Append it and continue.
- Otherwise **reject**. Append one token sampled from the **residual**
  distribution `max(0, targetProbs[i] − draftProbs[i])` (element-wise), using
  `uSample`, and **stop**. The remaining draft tokens are discarded.

If all $k$ drafts are accepted, append a **bonus** token sampled from
`targetProbs[k]` using `uSample`. Each step therefore yields between 1 and
$k + 1$ tokens.

**Sampling** with weights $w$ (the residual is not normalized) and a uniform
$v$ is inverse-CDF sampling: return the smallest index $j$ such that

$$
\sum_{l=0}^{j} w_l > v \sum_{l} w_l
$$

**Return `[outputTokens, numAccepted]`**, where `numAccepted` is the number of
draft tokens accepted.

Answers must match exactly. No `u[i]` is within a relative `1e-9` of its
$p / q$, and no sampling threshold $v \sum_l w_l$ is within
$10^{-9} \sum_l w_l$ of a cumulative sum, unless the two are exactly equal. In
that case every number involved has a power-of-two denominator, so
floating-point arithmetic computes the equality exactly.

## Constraints

- `1 <= k <= 16`, and the vocabulary size is `2 <= V <= 1000`
- `draftProbs` is `k × V` and `targetProbs` is `(k + 1) × V`. Every entry is
  in `[0, 1]`, and every row sums to `1` within `1e-9`
- `0 <= draftTokens[i] < V`, with `draftProbs[i][draftTokens[i]] > 0`
- `u` has `k` entries, and every entry of `u`, like `uSample`, is in `[0, 1)`

## Examples

**Example 1**
```
Input:  draftTokens = [2, 0], draftProbs = [[0.2, 0.3, 0.5], [0.6, 0.2, 0.2]],
        targetProbs = [[0.1, 0.3, 0.6], [0.3, 0.3, 0.4], [0.2, 0.5, 0.3]], u = [0.9, 0.7], uSample = 0.2
Output: [[2, 1], 1]
Explanation: at position 0, p/q = 0.6/0.5 ≥ 1, so token 2 is accepted. At
position 1, p/q = 0.3/0.6 = 0.5 ≤ 0.7, so token 0 is rejected. The residual
is [0, 0.1, 0.2]. With threshold 0.2 · 0.3 = 0.06 the cumulative sums are
0 and then 0.1 > 0.06, so token 1 is sampled. Argmax would wrongly pick
token 2.
```

**Example 2**
```
Input:  draftTokens = [1, 0], draftProbs = [[0.25, 0.5, 0.25], [0.5, 0.25, 0.25]],
        targetProbs = [[0.25, 0.25, 0.5], [0.5, 0.25, 0.25], [0.125, 0.125, 0.75]], u = [0.5, 0.9],
        uSample = 0.3
Output: [[2], 0]
Explanation: p/q = 0.25 / 0.5 = 0.5 exactly, and u = 0.5 is not strictly
smaller, so the first draft is rejected. The only residual mass is on token 2.
```

**Example 3**
```
Input:  draftTokens = [2, 2, 0], draftProbs = [[0.1, 0.2, 0.7], [0.2, 0.2, 0.6], [0.6, 0.3, 0.1]],
        targetProbs = [[0.2, 0.1, 0.7], [0.1, 0.1, 0.8], [0.7, 0.2, 0.1], [0.1, 0.3, 0.6]],
        u = [0.99, 0.5, 0.2], uSample = 0.2
Output: [[2, 2, 0, 1], 3]
Explanation: every draft has p ≥ q, so all three are accepted. The bonus
token is sampled from the last target row [0.1, 0.3, 0.6]: 0.1 ≤ 0.2 < 0.4,
so it is token 1.
```
