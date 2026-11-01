# Batch Norm: Training Forward and Backward

**Batch normalization** normalizes each feature (each column) over the batch,
then rescales it with learned parameters. Implement one training step for a
batch-norm layer: the forward pass, the backward pass, and the update of the
running statistics used later at inference.

`x` and `dy` are $N \times D$. Column $j$ is feature $j$, and `dy` is the
gradient of the loss $L$ with respect to the output $y$. With $\gamma$ =
`gamma`, $\beta$ = `beta` and $\epsilon$ = `eps`, each feature $j$ is
normalized over the $N$ rows, using the **biased** variance (divide by $N$):

$$
\begin{aligned}
\mu_j &= \frac{1}{N} \sum_{i=1}^{N} x_{ij} \\
\sigma_j^2 &= \frac{1}{N} \sum_{i=1}^{N} \left(x_{ij} - \mu_j\right)^2 \\
\hat x_{ij} &= \frac{x_{ij} - \mu_j}{\sqrt{\sigma_j^2 + \epsilon}} \\[1ex]
y_{ij} &= \gamma_j\, \hat x_{ij} + \beta_j
\end{aligned}
$$

**Backward.** The parameter gradients are sums over the batch:

$$
\begin{aligned}
\texttt{dbeta}_j &= \sum_{i=1}^{N} \texttt{dy}_{ij} \\
\texttt{dgamma}_j &= \sum_{i=1}^{N} \texttt{dy}_{ij}\, \hat x_{ij}
\end{aligned}
$$

`dx` is the full gradient through $\mu_j$ and $\sigma_j^2$, which both depend on
every row. With $g_{ij} = \gamma_j\, \texttt{dy}_{ij}$:

$$
\texttt{dx}_{ij} = \frac{1}{N \sqrt{\sigma_j^2 + \epsilon}}
\left( N g_{ij} \;-\; \sum_{k=1}^{N} g_{kj} \;-\; \hat x_{ij} \sum_{k=1}^{N} g_{kj}\, \hat x_{kj} \right)
$$

**Running statistics** (the PyTorch convention), with $\rho$ = `momentum`:

$$
\begin{aligned}
\texttt{newRunningMean}_j &= (1 - \rho)\, \texttt{runningMean}_j + \rho\, \mu_j \\
\texttt{newRunningVar}_j &= (1 - \rho)\, \texttt{runningVar}_j + \rho\, \sigma_j^2\, \frac{N}{N - 1}
\end{aligned}
$$

The running variance uses the **unbiased** batch variance (divide by $N - 1$),
even though normalization uses the biased one.

**Return `[y, dx, dgamma, dbeta, newRunningMean, newRunningVar]`**.

**Stability.** Some features have a large mean and a tiny spread (values near
`2000` that differ by `0.01`). The one-pass formula
$\sigma^2 = \overline{x^2} - \mu^2$ then loses almost every significant digit. Subtract the mean first.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `2 <= N <= 256` and `1 <= D <= 64`
- Every entry of `x` has absolute value `<= 10⁴`, and every entry of `dy` has
  absolute value `<= 10`
- `gamma`, `beta`, `runningMean` and `runningVar` each have `D` entries, with
  `|gamma|, |beta| <= 10`, `|runningMean| <= 10⁴` and `0 <= runningVar <= 10⁸`
- `1e-8 <= eps <= 0.1` and `0 <= momentum <= 1`
- All numbers are finite

## Examples

**Example 1**
```
Input:  x = [[1.0, 2.0], [3.0, 6.0]], gamma = [1.0, 1.0], beta = [0.0, 0.0],
        dy = [[1.0, 0.0], [0.0, 1.0]], eps = 1e-05, runningMean = [0.0, 0.0],
        runningVar = [1.0, 1.0], momentum = 0.1
Output: [[[-0.9999950000374997, -0.9999987500023437], [0.9999950000374997, 0.9999987500023437]],
         [[4.999925000854692e-06, -6.249976562573832e-07], [-4.999925000854692e-06, 6.249976562573832e-07]],
         [-0.9999950000374997, 0.9999987500023437], [1.0, 1.0], [0.2, 0.4],
         [1.1, 1.7000000000000002]]
Explanation: feature 0 has μ = 2 and σ² = 1, so x̂ ≈ [−1, 1]. With two rows
the unbiased variance is 2σ² = 2, so its running variance becomes
0.9 · 1 + 0.1 · 2 = 1.1. dx is almost zero: with only two rows, x̂ is ±1
whatever x is, so the output barely depends on x.
```

**Example 2**
```
Input:  x = [[0.0], [1.0], [2.0], [5.0]], gamma = [2.0], beta = [0.5],
        dy = [[1.0], [-1.0], [0.5], [0.25]], eps = 0.001, runningMean = [1.0],
        runningVar = [2.0], momentum = 0.5
Output: [[[-1.6377845593162195], [-0.5688922796581097], [0.5], [3.706676838974329]],
         [[0.8303111568973744], [-1.2883914922564252], [0.3340288373931593], [0.12405149796589139]],
         [-0.13361153495726374], [0.75], [1.5], [3.3333333333333335]]
```

**Example 3**
```
Input:  x = [[4.0, -1.0, 0.0], [4.0, 1.0, 2.0], [4.0, 0.0, 4.0]], gamma = [1.5, 1.0, -1.0],
        beta = [0.0, 1.0, 2.0], dy = [[1.0, 1.0, 1.0], [2.0, 0.0, -1.0], [-1.0, 2.0, 0.5]],
        eps = 0.01, runningMean = [0.0, 0.0, 0.0], runningVar = [1.0, 1.0, 1.0], momentum = 0.2
Output: [[[0.0, -0.21566134770966183, 3.222454913256092], [0.0, 2.215661347709662, 2.0],
          [0.0, 1.0, 0.7775450867439078]],
         [[5.0, -0.5988479545367794, -0.3571202346218244], [20.0, -0.6168133931728824, 0.7130986993993871],
          [-25.0, 1.2156613477096618, -0.35597846477756273]],
         [0.0, -1.2156613477096618, -0.6112274566280461], [2.0, 3.0, 0.5],
         [0.8, 0.0, 0.4], [0.8, 1.0, 1.6]]
Explanation: feature 0 is constant, so σ² = 0 and x̂ = 0. eps keeps the
division finite, and dx for that column is (1 / sqrt(0.01)) · (g − mean(g)).
```
