**Bagging** (bootstrap aggregating) trains many copies of a weak model, each on
a different resample of the training set, and lets them vote. Implement it
with a **decision stump** as the base model: a one-split tree that looks at a
single feature.

`X` holds the $n$ training rows ($d$ features each) and `y` their integer
labels. The resamples are given: `bootstraps[b]` is a list of row indices,
drawn **with replacement**, so an index can appear several times (that row
then counts that many times) and some rows don't appear at all.

**Fit one stump** on the multiset of rows a bootstrap selects:

1. For every feature $j$, sort the distinct values that feature takes in the
   sample. Every pair of neighbours $a < b$ gives a candidate threshold
   $t = (a + b)/2$.
2. A candidate $(j, t)$ sends a row **left** when $x_j \le t$ and **right**
   otherwise. Each side predicts its majority label (on a tie, the smaller
   label). Its **error** is the number of sample rows, duplicates included,
   whose label differs from their side's prediction.
3. Keep the candidate with the fewest errors. Break ties by the smaller
   feature index $j$, then by the smaller threshold $t$.
4. If no feature takes two distinct values in the sample, there are no
   candidates. The stump then predicts the sample's majority label (ties to the
   smaller label) for every input, and is reported as feature $-1$, threshold
   $0$.

**Predict.** Each stump votes for one label per row of `XTest`, and the
ensemble predicts the label with the most votes. On a tie, the smaller label.

**Return `[stumps, predictions]`:**

- `stumps`: one entry per bootstrap, in order, as
  `[feature, threshold, leftLabel, rightLabel]` (for a constant stump,
  `[-1, 0.0, label, label]`).
- `predictions`: the ensemble's label for each row of `XTest`.

You may use **numpy** and the Python standard library.

## Constraints

- `1 <= n <= 200`, `1 <= d <= 8`, `1 <= m <= 200` test rows
- Every feature value is finite with absolute value `<= 10⁴`
- Labels are integers with absolute value `<= 1000`
- `1 <= len(bootstraps) <= 30`; each bootstrap has between `1` and `n` indices,
  each in `[0, n)`

## Examples

**Example 1**
```
Input:  X = [[1.0], [2.0], [3.0], [4.0]], y = [0, 0, 1, 1],
        bootstraps = [[0, 1, 2, 3], [0, 0, 1, 2], [1, 3, 3, 3]], XTest = [[0.0], [2.2], [3.5]]
Output: [[[0, 2.5, 0, 1], [0, 2.5, 0, 1], [0, 3.0, 0, 1]], [0, 0, 1]]
Explanation: the second bootstrap sees x = 1, 1, 2, 3 with labels 0, 0, 0, 1.
Splitting at 1.5 makes 1 error and splitting at 2.5 makes none. The third sees
only x = 2 (label 0) and x = 4 three times (label 1), so its one threshold is 3.
```

**Example 2**
```
Input:  X = [[3.0], [1.0], [2.0], [1.0], [4.0]], y = [1, 1, 1, 4, 4],
        bootstraps = [[1, 3, 3, 2, 4], [4, 1, 3, 3, 1]], XTest = [[0.5], [2.0], [5.0]]
Output: [[[0, 1.5, 4, 1], [0, 2.5, 1, 4]], [1, 1, 1]]
Explanation: the first bootstrap holds x = 1 three times (labels 1, 4, 4),
x = 2 (label 1) and x = 4 (label 4); duplicates count. Threshold 1.5 puts
{1, 4, 4} left (predict 4, 1 error) and {1, 4} right (a tie, so predict 1,
1 error): 2 errors. Threshold 3 also makes 2 errors, and the smaller threshold
wins. The second bootstrap holds x = 1 four times (labels 1, 4, 4, 1) and x = 4
(label 4), so its left side is a tie and predicts 1. The stumps disagree on
0.5 and 5.0, and a tied vote goes to the smaller label.
```

**Example 3**
```
Input:  X = [[1.0, 1.0], [1.0, 2.0], [2.0, 1.0], [2.0, 2.0]], y = [1, 0, 0, 1],
        bootstraps = [[0, 1], [2, 3], [0, 1, 2, 3], [1, 1]], XTest = [[1.0, 1.0], [2.0, 2.0]]
Output: [[[1, 1.5, 1, 0], [1, 1.5, 0, 1], [0, 1.5, 0, 0], [-1, 0.0, 0, 0]], [0, 0]]
Explanation: in the first two bootstraps feature 0 is constant, so only
feature 1 can split. On all four rows (an XOR pattern) every split makes 2
errors, and the tie goes to feature 0; both of its sides are ties and predict
0. The last bootstrap is row 1 twice: no split exists, so it predicts its
majority label 0 everywhere.
```
