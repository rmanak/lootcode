Hire exactly `K` of the `N` workers. Worker `i` has `quality[i]` and minimum wage
`wage[i]`. Everyone in the group is paid in proportion to their quality, and each at
least their minimum wage. **Return the least total cost** (rounded to 5 decimals).

**Examples**
```
quality = [10,20,5], wage = [70,50,30], K = 2          ->  105.0
quality = [3,1,10,10,1], wage = [4,8,2,2,7], K = 3     ->  30.66667
```

**Constraints:** `1 <= K <= N <= 10^4`, `1 <= quality[i], wage[i] <= 10^4`.
