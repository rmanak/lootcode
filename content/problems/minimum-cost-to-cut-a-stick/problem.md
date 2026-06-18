A stick spans `[0, n]`. You must cut it at each position in `cuts` (in an order you
choose). Each cut costs the current length of the piece being cut, and splits it in
two. **Return the minimum total cost.**

**Examples**
```
n = 7, cuts = [1,3,4,5]    ->  16
n = 9, cuts = [5,6,1,4,2]  ->  22
```

**Constraints:** `2 <= n <= 10^6`, `1 <= len(cuts) <= min(n-1, 100)`,
`1 <= cuts[i] <= n-1`, all distinct.
