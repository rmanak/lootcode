There are `N` piles in a row; pile `i` has `stones[i]` stones. A move merges exactly
`K` consecutive piles into one, costing the total number of stones merged. **Return
the minimum total cost to merge all piles into one**, or `-1` if impossible.

**Examples**
```
stones = [3,2,4,1], K = 2     ->  20
stones = [3,2,4,1], K = 3     ->  -1
stones = [3,5,1,2,6], K = 3   ->  25
```

**Constraints:** `1 <= len(stones) <= 30`, `2 <= K <= 30`, `1 <= stones[i] <= 100`.
