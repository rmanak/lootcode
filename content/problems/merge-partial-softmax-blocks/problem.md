# Flash Attention: Merge Partial Softmax Blocks

Flash attention never materializes a full row of attention scores. It splits
the keys into blocks and computes a small summary of the softmax over each
block. It then **merges** the summaries into the exact result, as if the
softmax had been taken over all the keys at once. The merge is the heart of
the algorithm (the "online softmax"). Implement it.

For one query and one block of keys with scores $s_k$ and value vectors $v_k$,
the summary is `[m, l, o]`:

$$
\begin{aligned}
m &= \max_k s_k \\
l &= \sum_k e^{s_k - m} \\
o &= \frac{1}{l} \sum_k e^{s_k - m}\, v_k
\end{aligned}
$$

$m$ is the block's largest score, $l$ the softmax denominator relative to that
max (so $l \ge 1$), and $o$ the block's softmax-weighted average of its
values, a vector of length $d$.

A block whose keys are **all masked** (as in causal attention) has no
scores. Its summary is `[null, 0, [0, …, 0]]`, where `null` stands for
$m = -\infty$.

**Merging** a query's blocks $b$ gives the summary of all its keys together:
the largest max $M$, each block's denominator rescaled to the common max and
summed into $L$, the merged output $O$, and $\text{LSE}$, the log-sum-exp of
all the scores, which flash attention keeps for the backward pass:

$$
\begin{aligned}
M &= \max_b m_b \\
L &= \sum_b l_b\, e^{m_b - M} \\
O &= \frac{1}{L} \sum_b l_b\, e^{m_b - M}\, o_b \\
\text{LSE} &= M + \ln L
\end{aligned}
$$

Masked blocks contribute nothing. If **every** block of a query is masked,
the result is `[null, 0.0, null, [0.0, …, 0.0]]`.

Scores can be large (hundreds, even thousands), so never exponentiate an
$m$ on its own. Only exponentiate differences.

`queries` is a list. Each entry is one query's list of blocks `[m, l, o]`.
**Return** one `[M, L, LSE, O]` per query, in order.

You may use the Python standard library and **numpy**.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. `null` must be returned as `None`.

## Constraints

- `1 <= len(queries) <= 200`, and each query has `1` to `64` blocks
- Within a query, every `o` has the same length `d`, with `1 <= d <= 64`
- A live block has `|m| <= 10⁴`, `1 <= l <= 10⁶` and `|o[j]| <= 100`. A
  masked block is exactly `[null, 0, [0, …, 0]]`
- At most `2 · 10⁵` numbers in all the `o` vectors together

## Examples

**Example 1**
```
Input:  queries = [[[2.0, 1.5, [1.0, 0.0]], [3.0, 1.0, [0.0, 2.0]]]]
Output: [[3.0, 1.5518191617571635, 3.4394278954857405, [0.3555950173551955, 1.288809965289609]]]
Explanation: M = 3. The first block's mass rescales to 1.5 · e^(2 − 3) ≈ 0.5518,
so L ≈ 1.5518. O = (0.5518 · [1, 0] + 1 · [0, 2]) / 1.5518. LSE = 3 + ln(1.5518).
```

**Example 2**
```
Input:  queries = [[[null, 0.0, [0.0, 0.0]], [1.0, 2.0, [0.5, -0.5]]],
                   [[null, 0.0, [0.0, 0.0]], [null, 0.0, [0.0, 0.0]]]]
Output: [[1.0, 2.0, 1.6931471805599454, [0.5, -0.5]], [null, 0.0, null, [0.0, 0.0]]]
Explanation: the masked block changes nothing, so the first query is just
its live block, with LSE = 1 + ln 2. The second query sees no keys at all.
```

**Example 3**
```
Input:  queries = [[[0.0, 3.0, [1.0]], [5.0, 1.0, [2.0]], [-1.0, 2.0, [-3.0]]]]
Output: [[5.0, 1.025171345350589, 5.024859764815357, [1.9561035694491342]]]
Explanation: the masses are 3e⁻⁵, 1 and 2e⁻⁶ (about 0.0202, 1 and 0.0050),
so the block with the largest scores dominates the average:
(0.0202 · 1 + 2 − 0.0149) / 1.0252 ≈ 1.9561.
```
