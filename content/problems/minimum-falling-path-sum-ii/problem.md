`arr` is an `n x n` grid of integers. A **falling path with non-zero shifts** picks
exactly one element from each row so that no two elements chosen in adjacent rows
share the same column. Return the minimum possible sum of such a path.

**Example**
```
arr = [[1,2,3],
       [4,5,6],
       [7,8,9]]   ->  13     (path 1 -> 5 -> 7)
```

**Constraints:** `1 <= n <= 200`, `-99 <= arr[i][j] <= 99`.
