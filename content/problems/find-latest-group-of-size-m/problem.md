`arr` is a permutation of `1..n`. Start with `n` zero bits; at step `i` set bit
`arr[i]` to `1`. A *group* is a maximal run of `1`s. **Return the latest step at which
some group has length exactly `m`, or `-1` if none ever does.**

**Examples**
```
arr = [3,5,1,2,4], m = 1  ->  4
arr = [3,1,5,4,2], m = 2  ->  -1
arr = [1], m = 1          ->  1
```

**Constraints:** `1 <= len(arr) == n <= 10^5`, `arr` permutes `1..n`, `1 <= m <= n`.
