A recommender system logs **pairwise preferences**. Each example is a pair of
feature vectors $[x_1, x_2]$, and the user preferred item 1 over item 2 — say
they clicked restaurant 1 but not restaurant 2.

We score items with a linear function $s(x) = w \cdot x$ and want preferred
items to score higher. The model is trained by minimizing the **pairwise
logistic loss** (RankNet's loss with a linear scorer). With
$x^{(i)}_1, x^{(i)}_2$ the two vectors of `preferences[i]`, $m_i$ is the margin
of pair $i$, and the loss is the mean over all $N$ pairs:

$$
\begin{aligned}
m_i &= w \cdot \left(x^{(i)}_1 - x^{(i)}_2\right) \\
L(w) &= \frac{1}{N} \sum_{i=1}^{N} \log\left(1 + e^{-m_i}\right)
\end{aligned}
$$

A pair ranked correctly by a wide margin costs almost nothing. A pair ranked the
wrong way round costs roughly its margin.

Given `preferences` and a weight vector `w`, **return `[L(w), ∇L(w)]`**: the
loss $L(w)$ (a number) and its gradient $\nabla L(w)$ with respect to $w$ (a
list of $d$ numbers). This is the heart of one training step;
[Part II](/problems/pairwise-ranker-ii-training) uses it to train the model.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values, so
`return loss, grad` works as it is.

**Numerical stability matters.** Margins in the tests reach the tens of
thousands, positive and negative, and `exp` overflows a float past about 709.
Compute the loss without ever exponentiating a large positive number.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 200`, where `N = len(preferences)`
- Each `preferences[i]` is a pair `[x₁, x₂]` of vectors of the same length `d`,
  with `1 <= d <= 20`
- `len(w) == d`
- Every feature value and every `w[j]` is a finite number with absolute value
  `<= 100`

## Examples

**Example 1**
```
Input:  preferences = [[[2.0, 1.0, 3.0], [1.0, 1.0, 2.0]],
                       [[1.0, 1.0, 2.0], [2.0, 2.0, -3.0]]],
        w = [0.5, -0.5, 0.25]
Output: [0.3194000437301364,
         [-0.04906058099964908, 0.11135006941265443, -0.7171609974755757]]
Explanation: the differences x₁ − x₂ are [1, 0, 1] and [-1, -1, 5], so the
margins are 0.75 and 1.25, and L = (log(1 + e^-0.75) + log(1 + e^-1.25)) / 2.
Both pairs are already ranked correctly, so the loss is small.
```

**Example 2**
```
Input:  preferences = [[[2.0, 1.0, 3.0], [1.0, 1.0, 2.0]],
                       [[1.0, 1.0, 2.0], [2.0, 2.0, -3.0]]],
        w = [0.0, 0.0, 0.0]
Output: [0.6931471805599453, [0.0, 0.25, -1.5]]
Explanation: with w = 0 every margin is 0, so every pair costs log 2.
```

**Example 3**
```
Input:  preferences = [[[3.0], [1.0]]], w = [-1.0]
Output: [2.1269280110429727, [-1.7615941559557649]]
Explanation: the only pair is ranked the wrong way round (margin -2), so the
loss is large. Stepping against the gradient raises w, which fixes the ranking.
```
