A binary classifier outputs a **score** for each example, and a **threshold**
turns scores into predictions: predict `1` when `score >= threshold`, otherwise
`0`. A score exactly equal to the threshold is predicted positive.

Given the scores, the true labels (each `0` or `1`) and the threshold, count
the confusion matrix

| | label 1 | label 0 |
|---|---|---|
| **predicted 1** | `tp` (true positives) | `fp` (false positives) |
| **predicted 0** | `fn` (false negatives) | `tn` (true negatives) |

and compute, over the $N$ examples,

$$
\begin{aligned}
\text{precision} &= \frac{\texttt{tp}}{\texttt{tp} + \texttt{fp}} \\[1ex]
\text{recall} &= \frac{\texttt{tp}}{\texttt{tp} + \texttt{fn}} \\[1ex]
\text{f1} &= \frac{2 \cdot \text{precision} \cdot \text{recall}}{\text{precision} + \text{recall}} \\[1ex]
\text{accuracy} &= \frac{\texttt{tp} + \texttt{tn}}{N}
\end{aligned}
$$

Any of these that would be $0 / 0$ is $0$. This covers precision with no
positive predictions, recall with no positive labels, and F1 when precision
and recall are both 0.

**Return `[[tp, fp, fn, tn], precision, recall, f1, accuracy]`**.

The counts must match exactly. The other numbers are accepted when within a
relative `1e-6` (or an absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 10⁴`, where `scores` and `labels` both have `N` entries
- Every score is a finite number with absolute value `<= 10³`
- Every label is `0` or `1`
- `threshold` is a finite number with absolute value `<= 10³`

## Examples

**Example 1**
```
Input:  scores = [0.9, 0.8, 0.3, 0.6, 0.1], labels = [1, 0, 1, 1, 0], threshold = 0.5
Output: [[2, 1, 1, 1], 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6]
Explanation: the predictions are [1, 1, 0, 1, 0]. Examples 0 and 3 are true
positives, example 1 is a false positive, example 2 is a false negative, and
example 4 is a true negative.
```

**Example 2**
```
Input:  scores = [0.5, 0.2, 0.5], labels = [1, 0, 0], threshold = 0.5
Output: [[1, 1, 0, 1], 0.5, 1.0, 0.6666666666666666, 0.6666666666666666]
Explanation: both scores of 0.5 equal the threshold, so both are predicted
positive. F1 = 2 · 0.5 · 1 / 1.5 = 2/3.
```

**Example 3**
```
Input:  scores = [0.1, 0.4, 0.2], labels = [0, 1, 0], threshold = 0.9
Output: [[0, 0, 1, 2], 0.0, 0.0, 0.0, 0.6666666666666666]
Explanation: nothing is predicted positive, so precision is 0 / 0, which
counts as 0. Recall is 0 / 1 = 0, and F1 is 0 / 0, so 0.
```
