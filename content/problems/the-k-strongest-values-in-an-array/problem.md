A value `arr[i]` is *stronger* than `arr[j]` if `|arr[i] - m| > |arr[j] - m|`, where
`m` is the median of `arr`; ties (equal distance to `m`) are broken by the larger
value being stronger. The median is the element at index `(len(arr) - 1) // 2` of
the sorted array.

Return the `k` strongest values, in **any order**.

**Examples**
```
arr = [1,2,3,4,5], k = 2   ->  [5,1]   (median 3)
arr = [1,1,3,5,5], k = 2   ->  [5,5]   (median 3)
arr = [6,-3,7,2,11], k = 3 ->  [11,-3,2]   (median 6; any order accepted)
```

**Constraints:** `1 <= len(arr) <= 10^5`, `-10^5 <= arr[i] <= 10^5`,
`1 <= k <= len(arr)`.
