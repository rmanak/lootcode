There are `3n` piles. Repeatedly: pick any 3 remaining piles; Alice takes the
largest, **you** take the second largest, Bob takes the smallest. **Return the
maximum number of coins you can collect.** (Sort, then take every second pile from
the top, skipping the smallest `n`.)

**Examples**
```
piles = [2,4,1,2,7,8]          ->  9    (you take 7 and 2)
piles = [2,4,5]                ->  4
piles = [9,8,7,6,5,1,2,3,4]    ->  18
```

**Constraints:** `3 <= len(piles) <= 10^5`, `len(piles) % 3 == 0`,
`1 <= piles[i] <= 10^4`.
