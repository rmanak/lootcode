Before trusting a hand-derived gradient, you **check** it against a numerical
estimate. If the two disagree, the derivation (or the code) has a bug. Write
the check for this loss, L2-regularized logistic regression:

$$
\begin{aligned}
L(w) &= \frac{1}{N} \sum_{i=1}^{N} \log\left(1 + e^{-y_i\, (x_i \cdot w)}\right) \\
&\quad + \frac{\lambda}{2} \lVert w \rVert^2
\end{aligned}
$$

`X` has $N$ rows (examples) $x_i$ of $d$ features, `y` has the labels $y_i$
(each $+1$ or $-1$), $\lambda$ is `lam`, and `w` is the point to check at.

**Numerical gradient.** Use **central differences** with step $h$ = `h`. For
each coordinate $j$, with $e_j$ the unit vector along $j$:

$$
\texttt{numericGrad}_j = \frac{L(w + h\, e_j) - L(w - h\, e_j)}{2h}
$$

**Relative error** between the given `analyticGrad` (call it $a$) and the
numerical gradient $n$, with $\lVert \cdot \rVert$ the Euclidean norm:

$$
\texttt{relativeError} = \frac{\lVert a - n \rVert}{\lVert a \rVert + \lVert n \rVert}
$$

and $0$ if both norms are $0$.

**Return `[numericGrad, relativeError]`**.

**Evaluate the loss stably.** $x_i \cdot w$ can reach the hundreds, and
$e^{800}$ overflows a float. Compute $\log(1 + e^z)$ in a form that cannot
overflow, for example $\max(z, 0) + \log\left(1 + e^{-|z|}\right)$.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. When `analyticGrad` is correct, the
relative error is only truncation and rounding noise, around `1e-10`. Any
value of that size passes, because of the absolute `1e-9`.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every entry of `X` and `w` is a finite number with absolute value `<= 10`
- `y` has `N` entries, each `1` or `-1`
- `analyticGrad` has `d` finite entries with absolute value `<= 1000`
- `0 <= lam <= 10` and `1e-5 <= h <= 1e-2`
- The true gradient at `w` has a norm of at least `0.1`

## Examples

**Example 1**
```
Input:  X = [[1.0], [-1.0]], y = [1, -1], w = [0.5], lam = 0.0,
        analyticGrad = [-0.3775406687981454], h = 0.0001
Output: [[-0.3775406688941163], 1.2710007929567385e-10]
Explanation: both examples have margin 0.5, so L(w) = log(1 + e^(−w)) and the
true gradient is −1 / (1 + e^0.5). The analytic gradient is right, and the
relative error is just noise.
```

**Example 2**
```
Input:  X = [[1.0, 2.0], [0.5, -1.0], [-1.5, 0.5]], y = [1, -1, 1], w = [0.2, -0.3], lam = 0.1,
        analyticGrad = [0.205538340289, -0.700460865771], h = 0.001
Output: [[0.2255383327299243, -0.7304608416944802], 0.024125754727480846]
Explanation: this analytic gradient forgot the regularizer's term, lam · w =
[0.02, −0.03]. The difference shows up as a relative error of about 2%.
```

**Example 3**
```
Input:  X = [[2.0, 0.0], [0.0, 1.0]], y = [1, 1], w = [0.0, 0.0], lam = 0.0,
        analyticGrad = [-0.5, -0.5], h = 1e-05
Output: [[-0.49999999999772443, -0.24999999999608666], 0.1974530490858146]
Explanation: at w = 0 every sigmoid is 1/2, so the true gradient is
−(1/2) · mean(yᵢ · xᵢ) = [−0.5, −0.25]. The analytic gradient is wrong in its
second coordinate.
```
