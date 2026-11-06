Before most models can use a table, the numeric columns are standardized and
the categorical columns are one-hot encoded. The statistics must be **fit on
the training rows only** and then applied unchanged to the test rows.
Otherwise information leaks from the test set into training.

`train` and `test` are lists of rows. `columnTypes[j]` says whether column `j`
is `"numeric"` or `"categorical"`. A value may be missing, given as `None`
(`null` in the test data).

**Numeric columns.** From the $n$ non-missing training values $x_1, \dots, x_n$
of the column, compute the mean $\mu$ and the **population** standard
deviation $\sigma$ (divide by the count, not the count minus one):

$$
\begin{aligned}
\mu &= \frac{1}{n} \sum_{i=1}^{n} x_i \\
\sigma &= \sqrt{\frac{1}{n} \sum_{i=1}^{n} (x_i - \mu)^2}
\end{aligned}
$$

Each value $x$ becomes $(x - \mu) / \sigma$.
- A missing value (in train or test) is replaced by $\mu$, so it becomes $0$.
- If every non-missing training value in the column is the same, the column
  is constant and its output is $0$ for every row, train and test. Check
  equality of the values rather than `σ == 0`: three copies of `0.1` do not
  average to exactly `0.1` in floating point.

**Categorical columns.** The categories are the distinct non-missing values in
the training rows, **sorted** in ascending string order. A value becomes a
one-hot vector over those categories. A missing value, or a test value that
never appears in training, becomes all zeros.

Each output row is the concatenation of every column's features, in column
order. A numeric column gives one feature, and a categorical column gives one
feature per category.

**Return `[trainFeatures, testFeatures]`**, the transformed rows of `train` and
of `test`.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= len(columnTypes) <= 10`. Each entry is `"numeric"` or `"categorical"`.
- `train` and `test` each have between `1` and `200` rows, and every row has
  one value per column
- A numeric value is `None` or a finite number with absolute value `<= 10⁶`.
  Every numeric column has at least one non-missing training value.
- A categorical value is `None` or a string of 1 to 10 ASCII letters and digits
- A numeric column that is not constant has a training standard deviation of
  at least `1e-3`

## Examples

**Example 1**
```
Input:  train = [[1.0, "red"], [3.0, "blue"], [5.0, "red"]],
        test = [[4.0, "green"], [None, "blue"]], columnTypes = ["numeric", "categorical"]
Output: [[[-1.224744871391589, 0.0, 1.0], [0.0, 1.0, 0.0], [1.224744871391589, 0.0, 1.0]],
         [[0.6123724356957945, 0.0, 0.0], [0.0, 1.0, 0.0]]]
Explanation: the numeric column has μ = 3 and σ = sqrt(8/3). The categories
are ["blue", "red"], in sorted order. "green" never appears in training, so
it encodes as [0, 0]. The missing number becomes 0.
```

**Example 2**
```
Input:  train = [[2.0, None], [None, "b"], [6.0, "a"], [4.0, "b"]], test = [[None, None]],
        columnTypes = ["numeric", "categorical"]
Output: [[[-1.224744871391589, 0.0, 0.0], [0.0, 0.0, 1.0], [1.224744871391589, 1.0, 0.0],
          [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.0]]]
Explanation: μ and σ come from 2, 6 and 4 only. The missing training value is
skipped when fitting and then becomes 0. A missing category is not a category
of its own.
```

**Example 3**
```
Input:  train = [[7.0, 1.0], [7.0, 3.0]], test = [[0.0, 2.0], [7.0, None]],
        columnTypes = ["numeric", "numeric"]
Output: [[[0.0, -1.0], [0.0, 1.0]], [[0.0, 0.0], [0.0, 0.0]]]
Explanation: the first column is constant in training, so it is 0
everywhere, even for the test value 0.0.
```
