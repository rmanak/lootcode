# Linear Regression by Gradient Descent

**Linear regression** predicts a number as $w \cdot x + b$. Fit it by
minimizing the **mean squared error** with plain full-batch gradient descent,
exactly as follows. `X` has $N$ rows (examples) $x_i$ of $d$ features, `y` has
the $N$ targets $y_i$, and $\eta$ = `lr`.

Start from $w = 0$ ($d$ zeros) and $b = 0$, then repeat `steps` times. First
compute every example's residual $r_i$ and the mean squared error $L$:

$$
\begin{aligned}
r_i &= w \cdot x_i + b - y_i \\
L &= \frac{1}{N} \sum_{i=1}^{N} r_i^2
\end{aligned}
$$

Record $L$ (the loss **before** this step's update). Then take the gradients
of $L$ with respect to $w$ and $b$, and update both using the old $w$ and $b$:

$$
\begin{aligned}
g_w &= \frac{2}{N} \sum_{i=1}^{N} r_i\, x_i \\
g_b &= \frac{2}{N} \sum_{i=1}^{N} r_i \\
w &\leftarrow w - \eta\, g_w \\
b &\leftarrow b - \eta\, g_b
\end{aligned}
$$

Note the factor $2$: the loss is the plain mean of the squared residuals, not
half of it.

**Return `[w, b, lossHistory]`**: the final weights (a list of $d$ numbers),
the final bias, and the `steps` recorded losses in order.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Every test uses a learning rate small enough that gradient descent is stable
(it never blows up), though it may not have converged when it stops.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every feature is a finite number with absolute value `<= 100`
- `y` has `N` entries, each a finite number with absolute value `<= 1000`
- `0 < lr <= 1`, and `lr · λ < 1.9`, where `λ` is the largest eigenvalue of
  `(2/N) · Zᵀ·Z` and `Z` is `X` with a column of ones appended
- `1 <= steps <= 1000`

## Examples

**Example 1**
```
Input:  X = [[1.0], [2.0], [3.0]], y = [2.0, 4.0, 6.0], lr = 0.1, steps = 3
Output: [[1.7007407407407407], 0.6862222222222221,
         [18.666666666666668, 0.2962962962962968, 0.07337613168724277]]
Explanation: the data lies on y = 2x. The first loss is the mean of 4, 16 and
36. Three steps move w toward 2, though the bias is still absorbing part of the
fit.
```

**Example 2**
```
Input:  X = [[0.0, 1.0], [1.0, 0.0], [1.0, 1.0], [2.0, 1.0]], y = [1.0, 2.0, 2.5, 4.0],
        lr = 0.05, steps = 4
Output: [[0.8302142578125, 0.47642167968750004], 0.6082146484375001,
         [6.8125, 3.5605078125, 1.8802800048828119, 1.0109145988311767]]
```

**Example 3**
```
Input:  X = [[1.0], [-1.0]], y = [3.0, 1.0], lr = 0.25, steps = 2
Output: [[0.75], 1.5, [5.0, 1.25]]
Explanation: the residuals start at [−3, −1], so L = 5, gw = −2 and gb = −4.
The first step moves w to 0.5 and b to 1. The residuals become [−1.5, −0.5]
(L = 1.25), and the second step moves w to 0.75 and b to 1.5.
```
