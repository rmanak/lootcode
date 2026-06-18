You are given an array `arr` and a list of `queries`, each a triple
`[left, right, threshold]`. For each query, return the value that occurs **at least
`threshold` times** in the subarray `arr[left..right]` (inclusive), or `-1` if no
value does. It is guaranteed that `2 * threshold > right - left + 1`, so at most one
value can qualify per query. Return one answer per query, in order.

**Example**
```
arr = [1,1,2,2,1,1]
queries = [[0,5,4],[0,3,3],[2,3,2]]   ->  [1,-1,2]
```

**Constraints:** `1 <= len(arr) <= 2*10^4`, `1 <= arr[i] <= 2*10^4`,
`0 <= left <= right < len(arr)`, `2 * threshold > right - left + 1`.
