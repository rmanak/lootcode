# Softmax Cross-Entropy: Loss and Gradient

The last layer of a classifier outputs **logits**: one raw score per class for
each example. Softmax turns a row of logits into probabilities, and the
**cross-entropy loss** charges each example the negative log of the probability
it gave the correct class.

For a batch of $N$ examples over $C$ classes, write $z_i$ for the logits of
example $i$ (row `i` of `logits`) and $y_i$ for its label. Row $i$'s softmax
$p_i$ and the mean cross-entropy $L$ (natural log) are:

$$
\begin{aligned}
p_{ij} &= \frac{e^{z_{ij}}}{\sum_{k=1}^{C} e^{z_{ik}}} \\[1ex]
L &= -\frac{1}{N} \sum_{i=1}^{N} \log p_{i,\,y_i}
\end{aligned}
$$

A confident, correct example costs almost nothing. A confident, wrong one costs
roughly how far its correct logit trails the largest logit in its row.

Given `logits` (`N` rows of `C` numbers) and `labels` (`N` class indices),
**return `[L, grad]`**: the loss $L$ (a number) and its gradient with respect
to every logit, $\texttt{grad}[i][j] = \partial L / \partial z_{ij}$ (`N` rows
of `C` numbers, the same shape as `logits`). Together
they are the forward and backward pass of the loss layer in every
classification network.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values, so
`return loss, grad` works as it is.

**Numerical stability matters.** Logits in the tests reach ±1000. `exp`
overflows a float past about 709 and underflows to `0` below about −745, so a
direct translation of the formulas returns `nan` or `inf`. Your answer must be
exact, too: no epsilon fudge inside the `log`, because a confidently wrong
example has to cost its full amount.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 100`, where `N = len(logits) = len(labels)`
- `2 <= C <= 20`, and every row of `logits` has exactly `C` numbers
- Every logit is a finite number with absolute value `<= 1000`
- Each `labels[i]` is an integer with `0 <= labels[i] < C`

## Examples

**Example 1**
```
Input:  logits = [[2.0, 1.0, 0.1],
                  [0.5, 2.5, -1.0]],
        labels = [0, 2]
Output: [2.035104111700061,
         [[-0.17049943055701605, 0.12121648535235695, 0.0492829452046591],
          [0.058057267337070576, 0.42898840530422855, -0.4870456726412992]]]
Explanation: the softmax rows are about [0.659, 0.242, 0.099] and
[0.116, 0.858, 0.026]. Row 0 gives its label 0.659, costing 0.417; row 1 gives
its label only 0.026, costing 3.653. The loss is their mean.
```

**Example 2**
```
Input:  logits = [[3.0, 3.0, 3.0, 3.0]], labels = [1]
Output: [1.3862943611198906, [[0.25, -0.75, 0.25, 0.25]]]
Explanation: equal logits give every class probability 1/4, so the loss is
log 4. Stepping against the gradient raises the correct logit and lowers the
others.
```

**Example 3**
```
Input:  logits = [[30.0, 0.0, -30.0]], labels = [2]
Output: [60.00000000000009, [[0.9999999999999065, 9.35762296883931e-14, -1.0]]]
Explanation: the correct class trails the top logit by 60, so it gets
probability about e^-60 and the loss is about 60. Clipping the probability with
an epsilon (say log(p + 1e-12) ≈ 27.6) would be far off.
```
