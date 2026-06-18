**Return the number of contiguous subarrays of length exactly `k` whose average is
`>= threshold`.**

**Examples**
```
arr = [2,2,2,2,5,5,5,8], k = 3, threshold = 4              ->  3
arr = [1,1,1,1,1], k = 1, threshold = 0                    ->  5
arr = [11,13,17,23,29,31,7,5,2,3], k = 3, threshold = 5    ->  6
```

**Constraints:** `1 <= len(arr) <= 10^5`, `1 <= arr[i] <= 10^4`, `1 <= k <= len(arr)`,
`0 <= threshold <= 10^4`.
