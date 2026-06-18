`bloomDay[i]` is the day flower `i` blooms. A bouquet needs `k` adjacent bloomed
flowers; you want `m` bouquets. **Return the minimum number of days to wait**, or
`-1` if it is impossible.

**Examples**
```
bloomDay = [1,10,3,10,2], m = 3, k = 1   ->  3
bloomDay = [1,10,3,10,2], m = 3, k = 2   ->  -1
bloomDay = [7,7,7,7,12,7,7], m = 2, k = 3 ->  12
```

**Constraints:** `1 <= len(bloomDay) <= 10^5`, `1 <= bloomDay[i] <= 10^9`,
`1 <= m <= 10^6`, `1 <= k <= len(bloomDay)`.
