Solve the linear system $A x = b$ with one of the two classic **iterative**
methods. These are the building blocks behind large sparse solvers, and the
Gauss-Seidel sweep is the same "use the newest values" idea as asynchronous
value iteration.

Start from $x = 0$ ($n$ zeros). One **iteration** computes a new vector
$x^\text{new}$, one component at a time, for $i = 0, 1, \dots, n - 1$:

$$
x^\text{new}_i = \frac{1}{A_{ii}} \Big( b_i - \sum_{j \ne i} A_{ij}\, y_j \Big)
$$

- **`"jacobi"`**: $y$ is always the previous iterate $x$. Every component of
  the sweep uses only old values.
- **`"gauss-seidel"`**: $y_j$ is $x^\text{new}_j$ for $j < i$, the components
  already updated in this sweep, and $x_j$ for $j > i$.

After each iteration, let $\delta = \max_i \lvert x^\text{new}_i - x_i \rvert$,
the largest change in any component. Replace $x$ with $x^\text{new}$.
**Stop** as soon as $\delta <$ `tol`, or once `maxIterations` iterations have
run.

**Return `[x, iterations]`**, where `iterations` is the number of iterations
performed.

$A$ is strictly diagonally dominant by rows, so both methods converge.

You may use the Python standard library and **numpy**.

Integers must match exactly. Values are accepted within a relative `1e-6` (or
an absolute `1e-9`). No iteration's $\delta$ is within a relative `1e-9` of
`tol`.

## Constraints

- `1 <= n <= 30`, `A` is `n × n`, and `b` has `n` entries
- `|A[i][j]| <= 100` and `|b[i]| <= 1000`. In every row,
  `|A[i][i]| > Σ_{j ≠ i} |A[i][j]|`
- `method` is `"jacobi"` or `"gauss-seidel"`
- `1e-12 <= tol <= 1` and `1 <= maxIterations <= 1000`

## Examples

**Example 1**
```
Input:  A = [[4.0, 1.0], [2.0, 5.0]], b = [110.0, 190.0], method = "jacobi", tol = 5e-06, maxIterations = 100
Output: [[20.000000749999998, 30.0000008], 15]
Explanation: the first iteration gives [110/4, 190/5] = [27.5, 38], and the
second gives [(110 − 38)/4, (190 − 2 · 27.5)/5] = [18, 27]. The iterates
close in on the exact solution [20, 30]. The largest change first drops below
5e-6 at iteration 15 (about 3.8e-6, after 1.1e-5 at iteration 14).
```

**Example 2**
```
Input:  the same A, b and tol, method = "gauss-seidel"
Output: [[20.000000075, 29.999999969999998], 9]
Explanation: the first iteration gives x_new[0] = 110/4 = 27.5, and then
x_new[1] = (190 − 2 · 27.5)/5 = 27, which already uses the new 27.5. The
second gives [20.75, 29.7]. Using the fresh values converges in 9 iterations
instead of 15.
```

**Example 3**
```
Input:  A = [[10.0, -1.0, 2.0], [-1.0, 11.0, -1.0], [2.0, -1.0, 10.0]], b = [6.0, 25.0, -11.0],
        method = "jacobi", tol = 0.0001, maxIterations = 100
Output: [[1.0432848362598182, 2.269218329895499, -1.0817097237401818], 8]
Explanation: the first iteration gives [0.6, 25/11, −1.1]. At iteration 8 the
largest single change is about 9.8e-5 < 1e-4, so it stops there, even though
the length (2-norm) of the change vector, about 1.4e-4, is still above tol.
```
