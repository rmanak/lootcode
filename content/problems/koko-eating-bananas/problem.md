Koko has `len(piles)` piles of bananas; pile `i` has `piles[i]` bananas. The guards
return in `H` hours. At a chosen integer speed `K` bananas/hour she eats from one
pile each hour, finishing that pile early if it has fewer than `K` left (she does not
move on to another pile that hour). **Return the smallest `K`** that lets her eat
everything within `H` hours.

**Examples**
```
piles = [3,6,7,11], H = 8        ->  4
piles = [30,11,23,4,20], H = 5   ->  30
piles = [30,11,23,4,20], H = 6   ->  23
```

**Constraints:** `1 <= len(piles) <= 10^4`, `len(piles) <= H <= 10^9`,
`1 <= piles[i] <= 10^9`.
