Place `m` balls into baskets located at the distinct positions `position` so that
the **minimum** distance between any two balls is as **large** as possible. **Return
that maximum possible minimum distance.**

**Examples**
```
position = [1,2,3,4,7], m = 3            ->  3   (use 1, 4, 7)
position = [5,4,3,2,1,1000000000], m = 2 ->  999999999
```

**Constraints:** `2 <= len(position) <= 10^5`, `1 <= position[i] <= 10^9` distinct,
`2 <= m <= len(position)`.
