A row of `m` houses each needs one of `n` colors (`1..n`). `houses[i]` is the color of
house `i` (`0` = unpainted, must be painted; non-zero = already painted, keep it).
`cost[i][j]` is the cost to paint house `i` color `j+1`. A *neighborhood* is a maximal
run of equal colors. **Return the minimum total painting cost so there are exactly
`target` neighborhoods, or `-1` if impossible.**

**Examples**
```
houses=[0,0,0,0,0], cost=[[1,10],[10,1],[10,1],[1,10],[5,1]], m=5, n=2, target=3  ->  9
houses=[3,1,2,3], cost=[[1,1,1],[1,1,1],[1,1,1],[1,1,1]], m=4, n=3, target=3      ->  -1
```

**Constraints:** `1 <= m <= 100`, `1 <= n <= 20`, `1 <= target <= m`, `0 <= houses[i] <= n`,
`1 <= cost[i][j] <= 10^4`.
