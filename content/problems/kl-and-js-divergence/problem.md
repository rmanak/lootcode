The **Kullback–Leibler divergence** measures how much a distribution $P$
differs from a reference $Q$. It is the extra cost, in nats, of encoding
samples from $P$ with a code built for $Q$. It is not symmetric, which is why
the **Jensen–Shannon divergence**, a symmetric and always finite relative,
compares both to their average.

`p` and `q` are non-negative weights over the same $n$ outcomes. They need not
sum to $1$: first normalize each, $P_i = p_i / \sum_k p_k$ and
$Q_i = q_i / \sum_k q_k$. Then, with natural logs,

$$
\begin{aligned}
\operatorname{KL}(P \,\|\, Q) &= \sum_{i} P_i \log \frac{P_i}{Q_i} \\[1ex]
M &= \tfrac{1}{2}(P + Q) \\[1ex]
\operatorname{JS}(P, Q) &= \tfrac{1}{2} \operatorname{KL}(P \,\|\, M) + \tfrac{1}{2} \operatorname{KL}(Q \,\|\, M)
\end{aligned}
$$

An outcome with $P_i = 0$ contributes $0$ to $\operatorname{KL}(P \,\|\, \cdot)$
(the limit of $x \log x$). The tests promise that `p` and `q` are zero in
exactly the same positions, so both directions of KL are finite.

**Return `[KL(P‖Q), KL(Q‖P), JS(P, Q)]`.**

Weights can be as small as $10^{-12}$ next to weights of $10^{6}$: write each
term as $P_i (\log P_i - \log Q_i)$, or use logs of the raw weights, rather than
anything that can lose the small ones.

You may use **numpy** and the Python standard library.

## Constraints

- `1 <= n <= 10⁴`, and `p` and `q` have the same length
- Every weight is `0` or a number in `[10⁻¹², 10⁶]`
- Each of `p` and `q` has at least one positive weight, and `p[i] == 0` exactly
  when `q[i] == 0`

## Examples

**Example 1**
```
Input:  p = [0.1, 0.4, 0.5], q = [0.2, 0.3, 0.5]
Output: [0.04575811092471793, 0.05232481437645471, 0.01207862839058569]
Explanation: KL(P‖Q) = 0.1·log(0.5) + 0.4·log(4/3) + 0 ≈ 0.04576. The other
direction weights the log-ratios by Q instead, giving a different number.
```

**Example 2**
```
Input:  p = [2.0, 2.0, 0.0], q = [3.0, 1.0, 0.0]
Output: [0.14384103622589045, 0.13081203594113697, 0.03382207556860525]
Explanation: normalizing gives P = [0.5, 0.5, 0] and Q = [0.75, 0.25, 0]. The
third outcome is impossible under both and contributes nothing.
```

**Example 3**
```
Input:  p = [5.0], q = [0.001]
Output: [0.0, 0.0, 0.0]
Explanation: with one outcome, both normalize to [1]: the distributions are
identical.
```
