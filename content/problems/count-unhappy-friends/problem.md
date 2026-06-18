`n` friends (even `n`) are split into `n/2` pairs given by `pairs`.
`preferences[i]` lists the other friends from most to least preferred. Friend `x`
(paired with `y`) is **unhappy** if there is some friend `u` (paired with `v`) such
that `x` prefers `u` over `y` **and** `u` prefers `x` over `v`. **Return the number
of unhappy friends.**

**Examples**
```
n=4, preferences=[[1,2,3],[3,2,0],[3,1,0],[1,2,0]], pairs=[[0,1],[2,3]]  ->  2
n=2, preferences=[[1],[0]], pairs=[[1,0]]                                ->  0
n=4, preferences=[[1,3,2],[2,3,0],[1,3,0],[0,2,1]], pairs=[[1,3],[0,2]]  ->  4
```

**Constraints:** `2 <= n <= 500` (even), `preferences[i]` is a permutation of the
other `n-1` friends, each friend in exactly one pair.
