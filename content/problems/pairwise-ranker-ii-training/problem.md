# Pairwise Ranker II: Training

A recommender system logs **pairwise preferences**. Each example is a pair of
feature vectors $[x_1, x_2]$, and the user preferred item 1 over item 2 — say
they clicked restaurant 1 but not restaurant 2. Items are scored by a linear
function $s(x) = w \cdot x$, and the model is trained on the **pairwise logistic
loss**. With $x^{(i)}_1, x^{(i)}_2$ the two vectors of `preferences[i]` and
$m_i$ the margin of pair $i$, the loss is the mean over all $N$ pairs:

$$
\begin{aligned}
m_i &= w \cdot \left(x^{(i)}_1 - x^{(i)}_2\right) \\
L(w) &= \frac{1}{N} \sum_{i=1}^{N} \log\left(1 + e^{-m_i}\right)
\end{aligned}
$$

([Part I](/problems/pairwise-ranker-i-loss-and-gradient) computes this loss and
its gradient.) Now **train the model**: run gradient descent on $L$ and
**return the learned weight vector `w`**.

So that there is exactly one right answer, the training procedure is fixed,
with $\eta$ = `lr`:

1. Start from $w = 0$, a vector of $d$ zeros.
2. Repeat exactly `steps` times: compute the gradient $\nabla L(w)$ over **all
   $N$ pairs** at the current $w$, then update $w \leftarrow w - \eta\, \nabla L(w)$.
3. Return $w$, as a list of $d$ numbers.

There is no bias term, no regularization and no early stopping.

> **Why not just "the $w$ that minimizes $L$"?** Often there isn't one. If some
> $w$ ranks every pair correctly — as in Example 1 — then doubling it lowers the
> loss again, so the loss only approaches 0 as $w$ grows without bound. What you
> return would then depend on your learning rate, your step count and where you
> started. Fixing all three makes the answer well-defined.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 200`, where `N = len(preferences)`
- Each `preferences[i]` is a pair `[x₁, x₂]` of vectors of the same length `d`,
  with `1 <= d <= 10`
- Every feature value is a finite number with absolute value `<= 10`
- `0 < lr <= 1`
- `0 <= steps <= 1000`

## Examples

**Example 1**
```
Input:  preferences = [[[2.0, 1.0, 3.0], [1.0, 1.0, 2.0]],
                       [[1.0, 1.0, 2.0], [2.0, 2.0, -3.0]]],
        lr = 0.1, steps = 100
Output: [0.8121679467047354, -0.11611104444172111, 1.5088342133550618]
Explanation: w = [0, 0, 1] already ranks both pairs correctly, so this data has
no minimizer, and w keeps growing the longer you train. After exactly 100 steps
at lr = 0.1 it is the vector above.
```

**Example 2**
```
Input:  preferences = [[[2.0], [1.0]], [[1.0], [2.0]], [[3.0], [1.0]]],
        lr = 0.5, steps = 200
Output: [0.7563076126159645]
Explanation: the first two pairs contradict each other, so no w ranks every
pair correctly. This time the loss has a minimum, and 200 steps converge to it.
```
