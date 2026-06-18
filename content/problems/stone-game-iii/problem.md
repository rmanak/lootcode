Alice and Bob alternate (Alice first), each turn taking `1`, `2`, or `3` stones from
the front of the row; a player's score is the sum of values they take. Both play
optimally to maximize their own score. **Return `"Alice"`, `"Bob"`, or `"Tie"`.**

**Examples**
```
stoneValue = [1,2,3,7]   ->  "Bob"
stoneValue = [1,2,3,-9]  ->  "Alice"
stoneValue = [1,2,3,6]   ->  "Tie"
```

**Constraints:** `1 <= len(stoneValue) <= 5*10^4`, `-1000 <= stoneValue[i] <= 1000`.
