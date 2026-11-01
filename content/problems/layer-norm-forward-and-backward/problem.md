# LayerNorm: Forward and Backward

**Layer normalization** rescales each example's features to zero mean and unit
variance, then applies a learned per-feature scale `γ` and shift `β`. Every
transformer block uses it. Implement its forward pass and its backward pass.

`x` has $N$ rows (examples) of $D$ features. Each row $i$ is normalized on its
own, over its $D$ features, with $\gamma$ = `gamma`, $\beta$ = `beta` and
$\epsilon$ = `eps`. Row $i$ has mean $\mu_i$ and variance $\sigma_i^2$ (divide
by $D$, not $D - 1$):

$$
\begin{aligned}
\mu_i &= \frac{1}{D} \sum_{j=1}^{D} x_{ij} \\
\sigma_i^2 &= \frac{1}{D} \sum_{j=1}^{D} \left(x_{ij} - \mu_i\right)^2 \\
\hat x_{ij} &= \frac{x_{ij} - \mu_i}{\sqrt{\sigma_i^2 + \epsilon}} \\[1ex]
y_{ij} &= \gamma_j\, \hat x_{ij} + \beta_j
\end{aligned}
$$

For the backward pass you are given `dy`, the gradient
$\partial \ell / \partial y$ of some loss $\ell$ (same shape as `x`). Return the
gradients of $\ell$ with respect to the inputs and parameters:

- `dx`: $\partial \ell / \partial x$, an $N \times D$ matrix. Remember that
  $\mu_i$ and $\sigma_i^2$ depend on every entry of row $i$.
- `dgamma`: $\partial \ell / \partial \gamma$, $D$ numbers, summed over all $N$
  rows.
- `dbeta`: $\partial \ell / \partial \beta$, $D$ numbers, summed over all $N$
  rows.

**Return `[y, dx, dgamma, dbeta]`.**

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays are fine as return values.

**Numerical care matters.** Some test rows have a large mean and a tiny spread,
with `eps` as small as `1e-12`. Formulas for the variance that are equal on
paper are not equal in floating point there.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 64` and `1 <= D <= 64`
- `x` and `dy` are `N × D`; `gamma` and `beta` have `D` entries
- Every entry of `x` is a finite number with absolute value `<= 1000`
- Every entry of `gamma`, `beta` and `dy` is a finite number with absolute value
  `<= 10`
- `1e-12 <= eps <= 1`

## Examples

**Example 1**
```
Input:  x = [[1.0, 2.0, 3.0]], gamma = [1.0, 1.0, 1.0], beta = [0.0, 0.0, 0.0],
        dy = [[1.0, 0.0, 0.0]], eps = 1e-05
Output: [[[-1.2247356859083902, 0.0, 1.2247356859083902]],
         [[0.2041317996979287, -0.40824522863613005, 0.2041134289382015]],
         [-1.2247356859083902, 0.0, 0.0],
         [1.0, 0.0, 0.0]]
Explanation: μ = 2 and σ² = 2/3, so x̂ ≈ [−1.2247, 0, 1.2247]. The loss only
looks at y₀, but dx is non-zero everywhere: moving x₁ or x₂ shifts the mean
and the variance, and with them y₀.
```

**Example 2**
```
Input:  x = [[2.0, 4.0], [1.0, -1.0]], gamma = [2.0, 0.5], beta = [0.1, -0.1],
        dy = [[1.0, -2.0], [0.5, 3.0]], eps = 0.1
Output: [[[-1.8069251784911844, 0.3767312946227961],
          [2.0069251784911843, -0.5767312946227962]],
         [[0.13001762580621742, -0.13001762580621742],
          [-0.021669604301036247, 0.021669604301036247]],
         [-0.4767312946227961, -4.767312946227961],
         [1.5, 1.0]]
Explanation: both rows have variance 1, so x̂ = ±1/√1.1. A large eps visibly
shrinks the normalized values.
```

**Example 3**
```
Input:  x = [[0.0, 3.0, 1.0, 4.0], [5.0, 5.0, 5.0, 5.0]],
        gamma = [1.0, -1.0, 2.0, 0.5], beta = [0.0, 1.0, 0.0, -1.0],
        dy = [[1.0, 1.0, 1.0, 1.0], [2.0, -1.0, 0.5, 0.0]], eps = 1e-05
Output: [[[-1.264908534252813, 0.3675457328735935, -1.264908534252813, -0.3675457328735935],
          [0.0, 1.0, 0.0, -1.0]],
         [[-0.2687910396831634, -0.7747574891526277, 0.6166439223710259, 0.426904606464765],
          [316.2277660168379, 0.0, 0.0, -316.2277660168379]],
         [-1.264908534252813, 0.6324542671264065, -0.6324542671264065, 1.264908534252813],
         [3.0, 0.0, 1.5, 1.0]]
Explanation: row 1 is constant, so x̂ = 0 and y = β. Its dx is not zero,
though: with σ² = 0 the slope of x̂ is 1/√eps ≈ 316.
```
