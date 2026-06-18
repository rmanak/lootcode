Choose `i < j <= k`. Let `a = arr[i] ^ ... ^ arr[j-1]` and `b = arr[j] ^ ... ^ arr[k]`.
**Return the number of triples `(i, j, k)` with `a == b`.**

**Examples**
```
arr = [2,3,1,6,7]  ->  4
arr = [1,1,1,1,1]  ->  10
```

**Constraints:** `1 <= len(arr) <= 300`, `1 <= arr[i] <= 10^8`.
