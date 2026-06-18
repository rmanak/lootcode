Given an array `arr` of positive integers and a list of `queries` where
`queries[i] = [L, R]`, return for each query the XOR of `arr[L], arr[L+1], ...,
arr[R]`.

**Examples**
```
arr = [1,3,4,8], queries = [[0,1],[1,2],[0,3],[3,3]]   ->  [2,7,14,8]
arr = [4,8,2,10], queries = [[2,3],[1,3],[0,0],[0,3]]  ->  [8,0,4,4]
```

**Constraints:** `1 <= len(arr) <= 3*10^4`, `0 <= L <= R < len(arr)`.
