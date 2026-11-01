# Matrix Factorization by Gradient Descent

Collaborative filtering predicts how a user would rate an item from a few known
ratings. **Matrix factorization** gives every user $u$ a vector $U_u$ and every
item $i$ a vector $V_i$, each of length $k$. The predicted rating is their dot
product, $U_u \cdot V_i$.

Fit the factors with plain full-batch gradient descent, exactly as follows.
`ratings` is a list of observed triples `[u, i, r]`: user $u$ gave item $i$
the rating $r$. Only those entries count. Unrated (user, item) pairs are
**unknown, not zero**. `U` (users $\times$ $k$) and `V` (items $\times$ $k$)
are the starting factors.

With $\lambda$ = `reg`, the loss sums over the observed triples:

$$
\begin{aligned}
L &= \sum_{(u, i, r)} \left( U_u \cdot V_i - r \right)^2 \\
&\quad + \lambda \left( \lVert U \rVert^2 + \lVert V \rVert^2 \right)
\end{aligned}
$$

The penalty covers **every** row of $U$ and $V$, including users and items with
no ratings. $\lVert \cdot \rVert^2$ is the sum of squares of all entries.

Repeat `steps` times: record $L$ (**before** this step's update), then
compute the error $e_{ui} = U_u \cdot V_i - r$ of every observed triple, and,
with $\eta$ = `lr`, update both factors using the old $U$ and $V$:

$$
\begin{aligned}
G_{U_u} &= 2 \lambda\, U_u + 2 \sum_{(u, i, r)} e_{ui}\, V_i \\
G_{V_i} &= 2 \lambda\, V_i + 2 \sum_{(u, i, r)} e_{ui}\, U_u \\
U &\leftarrow U - \eta\, G_U \\
V &\leftarrow V - \eta\, G_V
\end{aligned}
$$

The first sum runs over the observed triples of user $u$, the second over those
of item $i$; a row with no ratings gets only the penalty's gradient.

**Return `[U, V, lossHistory]`**:
- `U` and `V`: the final factors, the same shapes as the inputs
- `lossHistory`: the `steps` recorded losses, in order

Every test uses a learning rate small enough that the loss stays bounded.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= users <= 50`, `1 <= items <= 50` and `1 <= k <= 10`, where `U` is
  users × k and `V` is items × k
- Every entry of `U` and `V` is a finite number with absolute value `<= 10`
- `1 <= len(ratings) <= 500`. Each triple has an integer user in `[0, users)`,
  an integer item in `[0, items)`, and a finite rating with absolute value
  `<= 10`. No (user, item) pair appears twice.
- `0 < lr <= 1` and `0 <= reg <= 10`
- `1 <= steps <= 500`

## Examples

**Example 1**
```
Input:  ratings = [[0, 0, 2.0]], U = [[1.0]], V = [[1.0]], lr = 0.1, reg = 0.0, steps = 2
Output: [[[1.3344]], [[1.3344]], [1.0, 0.31360000000000005]]
Explanation: the prediction starts at 1, so e = −1 and L = 1. Both gradients
are 2 · (−1) · 1 = −2, which moves U and V to 1.2. Now the prediction is 1.44,
e = −0.56 and L = 0.3136. Each factor then moves up by 0.1 · 2 · 0.56 · 1.2 =
0.1344.
```

**Example 2**
```
Input:  ratings = [[0, 0, 5.0], [0, 1, 3.0], [1, 1, 4.0]], U = [[1.0, 0.0], [0.0, 1.0]],
        V = [[1.0, 1.0], [1.0, 0.5]], lr = 0.05, reg = 0.1, steps = 3
Output: [[[1.990435705026769, 0.7751052653054322], [0.8538656364823259, 1.5335182104507965]],
         [[1.8633942416278106, 1.1391322102296022], [1.3359189483187448, 1.3160855450814164]],
         [32.775, 13.421545025625, 4.54473022551157]]
Explanation: user 1 has not rated item 0, so that entry adds nothing to the
loss or the gradients.
```

**Example 3**
```
Input:  ratings = [[0, 1, 1.0]], U = [[0.5], [2.0]], V = [[1.0], [0.5]], lr = 0.1, reg = 0.5,
        steps = 2
Output: [[[0.5485593750000001], [1.62]], [[0.81], [0.5485593750000001]],
         [3.3125, 2.825344140625]]
Explanation: user 1 and item 0 have no ratings, but the penalty still shrinks
them by a factor of 1 − 2 · lr · reg = 0.9 per step: 2 → 1.8 → 1.62 and
1 → 0.9 → 0.81.
```
