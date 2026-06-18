Given an array `arr` of even length, **return `true` if it can be split into
`len(arr)/2` pairs where each pair's sum is divisible by `k`**, else `false`.

**Examples**
```
arr = [1,2,3,4,5,10,6,7,8,9], k = 5  ->  true
arr = [1,2,3,4,5,6], k = 7           ->  true
arr = [1,2,3,4,5,6], k = 10          ->  false
arr = [-10,10], k = 2                ->  true
```

**Constraints:** `len(arr)` is even, `1 <= len(arr) <= 10^5`,
`-10^9 <= arr[i] <= 10^9`, `1 <= k <= 10^5`.
