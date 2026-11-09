The **entropy** of a model's next-token distribution measures how unsure it
is, and it is computed from the logits $x_1, \dots, x_n$ through a softmax:

$$
\begin{aligned}
p_i &= \frac{e^{x_i}}{\sum_{k=1}^{n} e^{x_k}} \\[1ex]
H &= -\sum_{i=1}^{n} p_i \log p_i
\end{aligned}
$$

(natural log). A vocabulary can be large enough that the logits arrive in
**chunks**, and you should not have to keep them. Implement a class that
consumes the logits chunk by chunk and can report the entropy of everything
seen so far at any time, using $O(1)$ memory:

- `StreamingEntropy()` starts with no logits.
- `update(chunk)` appends the logits in `chunk` (possibly an empty list).
- `entropy()` returns $H$ for all the logits appended so far. It is only called
  after at least one logit has arrived.

**Numerical stability is the point.** Logits in the tests reach magnitudes of
$10^{16}$, so $e^{x_i}$ overflows and even $\log p_i$ computed as
$\log(e^{x_i} / \sum e^{x_k})$ breaks. Keep a running maximum $m$ and, relative
to it, the running sums

$$
\begin{aligned}
s &= \sum_i e^{x_i - m} \\[1ex]
u &= \sum_i e^{x_i - m}\,(x_i - m)
\end{aligned}
$$

and work out how both must be rescaled when a new chunk raises $m$. Writing
$\log p_i = (x_i - m) - \log s$ shows that $H = \log s - u / s$.

Answers are accepted within a relative `1e-6` or an absolute `1e-9`.

## Constraints

- Every logit is finite with absolute value `<= 10¹⁶`
- At most `2000` calls in total and `20000` logits across all chunks
- `entropy` is only called once at least one logit has been appended

## Examples

**Example 1**

```
Input
["StreamingEntropy", "update", "entropy"]
[[], [[1.0, 2.0, 3.0]], []]

Output
[null, null, 0.8323955818399389]
```

Explanation: the softmax of `[1, 2, 3]` is about `[0.090, 0.245, 0.665]`, and
its entropy is about `0.832`.

**Example 2**

```
Input
["StreamingEntropy", "update", "entropy", "update", "entropy", "update", "entropy", "update", "entropy"]
[[], [[0.0, 0.0]], [], [[5.0]], [], [[]], [], [[-3.0, 5.0]], []]

Output
[null, null, 0.6931471805599453, null, 0.07986944651010895, null, 0.07986944651010895, null, 0.7348204516738862]
```

Explanation: two equal logits give $\log 2$. The `5` then raises the maximum
from `0` to `5` and dominates, so the entropy drops; the sums gathered relative
to the old maximum must be rescaled, not thrown away. An empty chunk changes
nothing. A second `5` splits the mass almost evenly between the two fives.

**Example 3**

```
Input
["StreamingEntropy", "update", "entropy", "update", "entropy", "update", "entropy"]
[[], [[1000.0, 1001.0]], [], [[999.0]], [], [[1e16, 1e16, 1e16]], []]

Output
[null, null, 0.5822031088882179, null, 0.8323955818399389, null, 1.0986122886681096]
```

Explanation: `[1000, 1001, 999]` is `[1, 2, 3]` shifted and reordered, so it has
the same entropy as Example 1, even though $e^{1000}$ overflows. The three
logits of $10^{16}$ then take all the mass between them: the entropy becomes
$\log 3$.
