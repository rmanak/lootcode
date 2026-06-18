From index `i` you may jump to `i ± x` for `1 <= x <= d` (staying in bounds), but
only if `arr[i]` is strictly greater than `arr[j]` and strictly greater than every
element strictly between `i` and `j`. Starting anywhere, **return the maximum number
of indices you can visit** (the start counts as one).

**Examples**
```
arr = [6,4,14,6,8,13,9,7,10,6,12], d = 2  ->  4
arr = [3,3,3,3,3], d = 3                   ->  1
arr = [7,6,5,4,3,2,1], d = 1               ->  7
```

**Constraints:** `1 <= len(arr) <= 1000`, `1 <= arr[i] <= 10^5`,
`1 <= d <= len(arr)`.
