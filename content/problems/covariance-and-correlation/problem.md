# Covariance and Correlation Matrices

Given a data matrix `X` with $n$ samples (rows) of $d$ features (columns),
compute its **covariance matrix** and its **correlation matrix**. With
$\bar x_j$ the average of column $j$ and $\delta$ = `ddof`:

$$
\begin{aligned}
\operatorname{cov}_{ij} &= \frac{1}{n - \delta} \sum_{k=1}^{n} \left(X_{ki} - \bar x_i\right) \left(X_{kj} - \bar x_j\right) \\[1ex]
\operatorname{corr}_{ij} &= \frac{\operatorname{cov}_{ij}}{\sqrt{\operatorname{cov}_{ii}\, \operatorname{cov}_{jj}}}
\end{aligned}
$$

`ddof = 1` gives the unbiased sample covariance (numpy's `np.cov` default),
and `ddof = 0` the population covariance.

**Constant columns.** A column whose values are all equal has zero variance,
so its correlations are undefined. Report every entry of its correlation row
and column as $0$, **including its own diagonal entry**. Its covariances are
$0$ as usual.

Columns can sit far from zero, for example values near $10^8$ that vary by
about $1$. Compute the variance in a numerically stable way.

**Return `[cov, corr]`**, two $d \times d$ matrices.

You may use the Python standard library and **numpy**. A numpy array is fine
as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= n <= 1000` and `1 <= d <= 20`
- Every value in `X` is finite with absolute value `<= 10⁹`
- `ddof` is `0` or `1`, and `n − ddof >= 1`

## Examples

**Example 1**
```
Input:  X = [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]], ddof = 1
Output: [[[1.0, 2.0], [2.0, 4.0]], [[1.0, 1.0], [1.0, 1.0]]]
Explanation: the deviations are [−1, 0, 1] and [−2, 0, 2]. Dividing by
n − 1 = 2 gives variances 1 and 4 and covariance 2. The columns are perfectly
correlated.
```

**Example 2**
```
Input:  X = [[1.0, 5.0, 0.0], [3.0, 5.0, 2.0], [5.0, 5.0, 1.0], [7.0, 5.0, 3.0]], ddof = 0
Output: [[[5.0, 0.0, 2.0], [0.0, 0.0, 0.0], [2.0, 0.0, 1.25]],
         [[1.0, 0.0, 0.8], [0.0, 0.0, 0.0], [0.8, 0.0, 1.0]]]
Explanation: dividing by n = 4 gives var₀ = 20/4 = 5, var₂ = 5/4 = 1.25 and
cov₀₂ = 8/4 = 2, so corr₀₂ = 2 / sqrt(5 · 1.25) = 0.8. Column 1 is constant,
so its whole correlation row and column, diagonal included, are 0.
```

**Example 3**
```
Input:  X = [[0.1, -1.0], [0.1, 1.0], [0.1, 3.0]], ddof = 1
Output: [[[0.0, 0.0], [0.0, 4.0]], [[0.0, 0.0], [0.0, 1.0]]]
Explanation: column 0 is constant. In floating point, 0.1 + 0.1 + 0.1 divided
by 3 is not exactly 0.1. A tiny nonzero variance would make its correlation
come out as 1 instead of the required 0, so detect constant columns by their
values, not by their variance.
```
