**K-fold cross-validation** splits a dataset into $k$ folds. Each fold takes a
turn as the validation set. A **stratified** split keeps every class's share
roughly the same in every fold, which matters when some classes are rare.

Split the indices $0, \dots, N - 1$ into `k` folds, exactly as follows.
`labels[i]` is example `i`'s class. Instead of drawing a random shuffle, the
shuffle is the input `perm`, a permutation of $0, \dots, N - 1$.

```
pointer = 0
for each class label, in ascending order of the label value:
    take the indices of that class, in the order they appear in perm
    for each of them:
        put it in fold `pointer`
        pointer = (pointer + 1) mod k
```

Do **not** reset `pointer` between classes. Because the deal continues, the
fold sizes differ by at most one.

**Return the `k` folds**, fold `0` first. Each fold is a list of indices sorted
in ascending order.

## Constraints

- `2 <= N <= 10⁴`, where `labels` has `N` entries
- Every label is an integer in `[0, 10⁶]`
- `2 <= k <= min(N, 100)`
- `perm` is a permutation of `0 … N − 1`

## Examples

**Example 1**
```
Input:  labels = [0, 1, 0, 1, 0, 1], k = 3, perm = [5, 2, 0, 3, 4, 1]
Output: [[2, 5], [0, 3], [1, 4]]
Explanation: class 0 holds indices 0, 2 and 4. In perm they appear in the order
2, 0, 4, so they go to folds 0, 1 and 2. Class 1's indices appear in the order
5, 3, 1, and the pointer continues at fold 0.
```

**Example 2**
```
Input:  labels = [1, 1, 1, 0, 0], k = 2, perm = [0, 1, 2, 3, 4]
Output: [[0, 2, 3], [1, 4]]
Explanation: class 0 comes first because 0 < 1, even though class 1 appears
first in the data. Indices 3 and 4 go to folds 0 and 1. Then 0, 1 and 2 go to
folds 0, 1 and 0.
```

**Example 3**
```
Input:  labels = [7, 2, 7, 7, 2, 9, 7], k = 3, perm = [6, 0, 3, 1, 5, 2, 4]
Output: [[0, 1, 5], [3, 4], [2, 6]]
Explanation: class 2 (indices 1, 4) fills folds 0 and 1. Class 7, in perm
order 6, 0, 3, 2, goes to folds 2, 0, 1, 2. Class 9 (index 5) goes to fold 0.
```
