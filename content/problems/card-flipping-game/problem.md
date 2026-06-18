Each card `i` shows `fronts[i]` and `backs[i]`. You may flip any cards, then choose
one card; the number `X` on its back is *good* if `X` appears on no card's front.
**Return the smallest good number**, or `0` if none exists. (A number that is equal
on both sides of some card can never be good.)

**Example**
```
fronts = [1,2,4,4,7], backs = [1,3,4,1,3]  ->  2
```

**Constraints:** `1 <= len(fronts) == len(backs) <= 1000`,
`1 <= fronts[i], backs[i] <= 2000`.
