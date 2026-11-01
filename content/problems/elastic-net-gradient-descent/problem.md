# Elastic Net by Subgradient Descent

**Elastic net** regression adds both an L1 penalty (which pushes weights to
exactly zero) and an L2 penalty (which shrinks them) to least squares. Fit it
with full-batch **subgradient** descent, exactly as follows.

`X` has $N$ rows (examples) $x_i$ of $d$ features, and `y` has the $N$ targets
$y_i$. With $\alpha$ = `alpha`, $\rho$ = `l1Ratio` and the residuals
$r_i = w \cdot x_i + b - y_i$, the objective is

$$
\begin{aligned}
J(w, b) &= \frac{1}{2N} \sum_{i=1}^{N} r_i^2 \\
&\quad + \alpha \left( \rho \sum_{j} |w_j| + \frac{1 - \rho}{2} \sum_{j} w_j^2 \right)
\end{aligned}
$$

The mean squared error is **halved**, and the **intercept $b$ is not
penalized**. $|w_j|$ has no derivative at $0$, so use the subgradient
$\operatorname{sign}(w_j)$ with **$\operatorname{sign}(0) = 0$**.

Start from $w = 0$ ($d$ zeros) and $b = 0$, then repeat `steps` times: record
$J(w, b)$ (**before** this step's update), then, with $\eta$ = `lr`, update
both parameters using the old $w$ and $b$:

$$
\begin{aligned}
g_w &= \frac{1}{N} \sum_{i=1}^{N} r_i\, x_i \\
&\quad + \alpha \big( \rho \operatorname{sign}(w) + (1 - \rho)\, w \big) \\
g_b &= \frac{1}{N} \sum_{i=1}^{N} r_i \\
w &\leftarrow w - \eta\, g_w \\
b &\leftarrow b - \eta\, g_b
\end{aligned}
$$

$\operatorname{sign}$ applies to each weight separately. Since $w$ starts at
zero, the L1 term has no effect on the first step. A weight whose feature is
all zeros stays at exactly $0$.

**Return `[w, b, lossHistory]`**: the final weights ($d$ numbers), the final
bias, and the `steps` recorded objective values in order.

Subgradient descent with a fixed step does not settle on the optimum. Weights
that should be zero keep jumping back and forth across zero, so the history
need not go down at every step. Follow the update exactly. The tests are built
so that no weight $\operatorname{sign}$ reads is within `1e-9` of zero unless
it is exactly zero.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every feature is a finite number with absolute value `<= 100`
- `y` has `N` entries, each a finite number with absolute value `<= 1000`
- `0 <= alpha <= 100` and `0 <= l1Ratio <= 1`
- `0 < lr <= 1`, and `lr · (λ + alpha · (1 − l1Ratio)) < 1.9`, where `λ` is the
  largest eigenvalue of `(1/N) · Zᵀ·Z` and `Z` is `X` with a column of ones
  appended
- `1 <= steps <= 1000`

## Examples

**Example 1**
```
Input:  X = [[1.0], [2.0], [3.0]], y = [2.0, 4.0, 6.0], alpha = 1.0, l1Ratio = 0.5,
        lr = 0.1, steps = 3
Output: [[1.3749814814814816], 0.6651111111111111,
         [9.333333333333334, 2.5659259259259253, 1.6270723251028805]]
Explanation: the residuals start at [−2, −4, −6], so J = 56 / 6. On the first
step w = 0, so both penalty terms of gw are 0: gw = −28/3 and gb = −4, which
moves w to 0.9333… and b to 0.4. From the second step on, the penalty pulls w
back toward zero.
```

**Example 2**
```
Input:  X = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], y = [3.0, -1.0, 2.0], alpha = 0.5,
        l1Ratio = 1.0, lr = 0.2, steps = 4
Output: [[0.6740444444444446, -0.10395061728395062], 0.6191407407407408,
         [2.3333333333333335, 1.7525925925925925, 1.5208609053497943, 1.4297521938728852]]
Explanation: l1Ratio = 1 makes this the lasso: only the L1 term is used.
```

**Example 3**
```
Input:  X = [[2.0, 0.0], [-1.0, 0.0], [0.5, 0.0]], y = [1.0, -2.0, 0.0], alpha = 0.2,
        l1Ratio = 0.75, lr = 0.25, steps = 3
Output: [[0.5885416666666666, 0.0], -0.28515625,
         [0.8333333333333334, 0.5006944444444446, 0.37889539930555544]]
Explanation: the second feature is always 0, so its gradient is always 0, and
with sign(0) = 0 its weight never moves.
```
