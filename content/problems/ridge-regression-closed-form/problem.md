# Ridge Regression in Closed Form

**Ridge regression** is linear regression with an L2 penalty on the weights. It
shrinks the weights toward zero, and it still has a unique answer when the
features are collinear or there are more features than examples.

`X` has $N$ rows (examples) $x_i$ of $d$ features, and `y` has the $N$ targets
$y_i$. With $\lambda$ = `lam`, find the weights $w$ (a list of $d$ numbers) and
the intercept $b$ that minimize

$$
J(w, b) = \sum_{i=1}^{N} \left(w \cdot x_i + b - y_i\right)^2 + \lambda \sum_{j=1}^{d} w_j^2
$$

The loss is the plain **sum** of squared residuals (not the mean), and the
**intercept is not penalized**. Only the weights are.

**Return `[w, b]`.**

Compute the exact minimizer in closed form. Gradient descent will not reach
`1e-6` accuracy. Any route to the exact answer is fine.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `2 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every feature is a finite number with absolute value `<= 100`
- `y` has `N` entries, each a finite number with absolute value `<= 1000`
- `0 <= lam <= 10⁴`
- The minimizer is unique and well conditioned. Let `Xc` be `X` with each
  column's mean subtracted. Then the matrix `Xcᵀ·Xc + lam·I` has a condition
  number of at most `10⁶`. In particular, when `lam = 0` the columns of `X`
  together with a column of ones are linearly independent.

## Examples

**Example 1**
```
Input:  X = [[1.0], [2.0], [3.0], [4.0]], y = [3.0, 5.0, 7.0, 9.0], lam = 0.0
Output: [[2.0], 1.0]
Explanation: with no penalty this is ordinary least squares, and the data lies
exactly on y = 2x + 1.
```

**Example 2**
```
Input:  X = [[1.0], [2.0], [3.0], [4.0]], y = [3.0, 5.0, 7.0, 9.0], lam = 5.0
Output: [[1.0], 3.5]
Explanation: the penalty halves the slope, from 2 to 1. The intercept is free,
so it moves until the fitted line passes through the means of the data,
(2.5, 6): b = 6 − 2.5 · 1 = 3.5.
```

**Example 3**
```
Input:  X = [[0.0, 1.0], [1.0, 0.0], [1.0, 1.0], [2.0, 3.0]], y = [1.0, 1.0, 3.0, 6.0],
        lam = 1.0
Output: [[0.9245283018867925, 1.1132075471698113], 0.4339622641509435]
Explanation: the exact answer is w = [49/53, 59/53] and b = 23/53.
```
