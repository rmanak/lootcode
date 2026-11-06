**Pegasos** trains a linear support vector machine by stochastic subgradient
descent on the regularized hinge loss, where $\lambda$ = `lam`, $x_i$ =
`X[i]` and $y_i$ = `y[i]`:

$$
\frac{\lambda}{2} \lVert w \rVert^2 + \frac{1}{N} \sum_{i=1}^{N} \max\big(0,\; 1 - y_i\, (w \cdot x_i)\big)
$$

Each step looks at one example. Instead of drawing the examples at random, the
indices come in as `order`: step $t$ (counting from $t = 1$) uses example
$i$ = `order[t − 1]`. Run the algorithm exactly as follows.

Start from $w = 0$ ($d$ zeros). For $t = 1, 2, \dots, T$, where $T$ =
`len(order)`, take the step size $\eta_t$ and the margin $m$ of example $i$,
computed with $w$ from **before** this step:

$$
\begin{aligned}
\eta_t &= \frac{1}{\lambda t} \\
m &= y_i\, (w \cdot x_i)
\end{aligned}
$$

then update

$$
w \leftarrow
\begin{cases}
(1 - \eta_t \lambda)\, w + \eta_t\, y_i\, x_i & \text{if } m < 1 \\
(1 - \eta_t \lambda)\, w & \text{otherwise}
\end{cases}
$$

The regularizer shrinks $w$ on every step. Only examples inside the margin
(strictly $m < 1$) also pull $w$ toward them. An example with margin
**exactly** $1$ does not count as a violation. There is **no bias** term and
**no projection** step. Labels are $+1$ or $-1$.

**Return `w`**, a list of $d$ numbers.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. In the tests, a margin is either more
than `1e-6` away from $1$, or exactly $1$ at a step where floating-point
arithmetic computes it without rounding.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every feature is a finite number with absolute value `<= 100`
- `y` has `N` entries, each `1` or `-1`
- `1e-4 <= lam <= 10`
- `1 <= len(order) <= 2000`, and every entry of `order` is an index in `[0, N)`

## Examples

**Example 1**
```
Input:  X = [[2.0], [-1.0], [1.0]], y = [1, -1, 1], lam = 0.5, order = [0, 1, 2, 0]
Output: [1.0]
Explanation:
t = 1, i = 0: eta = 2. The margin is 0 < 1, so w = 0 + 2 · 1 · 2 = 4.
t = 2, i = 1: eta = 1. The margin is −1 · (4 · −1) = 4, so w only shrinks: w = (1 − 0.5) · 4 = 2.
t = 3, i = 2: eta = 2/3. The margin is 2, so w = (1 − 1/3) · 2 = 4/3.
t = 4, i = 0: eta = 1/2. The margin is 8/3, so w = (1 − 1/4) · 4/3 = 1.
```

**Example 2**
```
Input:  X = [[1.0, 0.0], [1.0, 1.0], [-1.0, -2.0], [0.0, -1.0]], y = [1, 1, -1, -1],
        lam = 1.0, order = [0, 1, 2, 3, 1]
Output: [0.4, 0.6000000000000001]
Explanation: step 1 sets w = [1, 0]. At step 2 the margin of example 1 is
exactly 1, which is not a violation, so w only shrinks to [0.5, 0]. Steps 3 and
4 are violations, and step 5 (margin 1.25) only shrinks.
```

**Example 3**
```
Input:  X = [[1.0, 2.0], [2.0, -1.0], [-1.5, 0.5]], y = [1, -1, -1], lam = 0.1,
        order = [0, 2, 1, 0, 1, 2]
Output: [0.8333333333333339, 4.166666666666667]
```
