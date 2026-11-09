An A/B test compares a metric between a control group ($0$) and a treatment
group ($1$). The headline number is the difference of the group means, and
two classic resampling methods say how uncertain it is: a **bootstrap**
confidence interval and a **jackknife** standard error. Compute all three.

Row $i$ of the experiment is `groups[i]` (`0` or `1`) and `values[i]`. Let
$x_0$ be the values of group $0$ in row order ($n_0$ of them), and $x_1$
those of group $1$ ($n_1$). The estimate is

$$
\hat\theta = \operatorname{mean}(x_1) - \operatorname{mean}(x_0)
$$

**Stratified bootstrap.** The random draws are given. Replicate $r$
resamples each group separately, keeping its size: `resample0[r]` lists $n_0$
indices into $x_0$ (positions $0$ to $n_0 - 1$, repeats allowed) and
`resample1[r]` lists $n_1$ indices into $x_1$. Its estimate $\theta^*_r$ is the
mean of the selected $x_1$ values minus the mean of the selected $x_0$ values.

The **percentile interval** at level $1 - \alpha$ runs from the $\alpha/2$
quantile to the $1 - \alpha/2$ quantile of the $B$ replicate estimates. The
$q$ quantile is found by sorting the estimates into $s_0 \le \dots \le s_{B-1}$,
setting $h = (B - 1)q$, and interpolating linearly between $s_{\lfloor h \rfloor}$
and $s_{\lceil h \rceil}$:

$$
Q(q) = s_{\lfloor h \rfloor} + (h - \lfloor h \rfloor)\,(s_{\lceil h \rceil} - s_{\lfloor h \rfloor})
$$

(This is numpy's default `percentile`.)

**Jackknife.** For each of the $n = n_0 + n_1$ rows, let $\theta_{(i)}$ be the
estimate with row $i$ removed (from whichever group it belongs to), and
$\bar\theta$ the mean of these $n$ values. Then

$$
\operatorname{SE} = \sqrt{\frac{n - 1}{n} \sum_{i} \left(\theta_{(i)} - \bar\theta\right)^2}
$$

With up to $2 \cdot 10^4$ rows, recomputing every mean from scratch is too slow:
each leave-one-out mean follows from the full group mean in $O(1)$.

**Precision.** The metric can carry a large offset (latencies in
nanoseconds, timestamps, balances in cents), with values near $10^9$ that
differ only in their last few digits. Every quantity above is a difference of
means, so it does not change if one constant is subtracted from all values,
and subtracting a constant close to the data (the overall mean, say) is exact
in floating point. Do that first. Otherwise the digits that make up the
answer are rounded away: a group sum near $10^{13}$ keeps barely three
decimals, and the leave-one-out form $(\text{sum} - x)/(k - 1)$ loses the
rest.

**Return `[estimate, ciLower, ciUpper, jackknifeSE]`**. Answers are accepted
within a relative error of $10^{-6}$.

You may use **numpy** and the Python standard library.

## Constraints

- `4 <= n <= 2·10⁴`; each group has at least `2` rows; every value is finite
  with absolute value `<= 10⁹`
- `1 <= B <= 2000` replicates, `B · n <= 2·10⁵`; every index is in range
- `0 < alpha < 1`

## Examples

**Example 1**
```
Input:  groups = [0, 0, 1, 1], values = [1.0, 1.0, 3.0, 3.0],
        resample0 = [[0, 1], [1, 1], [0, 0]], resample1 = [[1, 0], [0, 0], [1, 1]], alpha = 0.05
Output: [2.0, 2.0, 2.0, 0.0]
Explanation: every value in a group is the same, so every resample and every
leave-one-out estimate is exactly 2.
```

**Example 2**
```
Input:  groups = [1, 0, 0, 1, 0, 1], values = [5.0, 2.0, 4.0, 7.0, 0.0, 6.0],
        resample0 = [[0, 0, 0], [0, 1, 2], [2, 2, 1], [1, 1, 1], [2, 0, 1]],
        resample1 = [[0, 1, 2], [2, 2, 2], [0, 0, 1], [1, 1, 0], [0, 2, 2]], alpha = 0.2
Output: [4.0, 2.8666666666666667, 4.2, 1.4433756729740645]
Explanation: x0 = [2, 4, 0] and x1 = [5, 7, 6], so the estimate is 6 − 2 = 4.
The first replicate is mean(5, 7, 6) − mean(2, 2, 2) = 4. The sorted
replicates are 2.333…, 3.666…, 4, 4, 4.333…; the 0.1 quantile sits at h = 0.4,
giving 2.333… + 0.4 · 1.333… = 2.8666…, and the 0.9 quantile at h = 3.6 gives 4.2.
```

**Example 3**
```
Input:  groups = [0, 1, 0, 1, 1], values = [10.0, 12.0, 14.0, 20.0, 13.0],
        resample0 = [[1, 0], [0, 0], [1, 1], [0, 1]], resample1 = [[2, 2, 0], [1, 0, 2], [1, 1, 1], [0, 2, 1]],
        alpha = 0.5
Output: [3.0, 2.4166666666666665, 5.25, 3.7416573867739413]
Explanation: the estimate is 15 − 12 = 3. Removing a row of group 0 leaves
one value of 10 or 14 (estimates 5 and 1); removing 12, 20 or 13 from group 1
gives 4.5, 0.5 and 4. Their mean is 3, and the SE is
√(4/5 · (4 + 4 + 2.25 + 6.25 + 1)) = √14 ≈ 3.742.
```
