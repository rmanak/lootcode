There are several cards in a row; card `i` is worth `cardPoints[i]` points. In one
step you take a card from the **beginning or the end** of the row, and you take
exactly `k` cards. **Return the maximum total points** you can obtain.

The `k` cards you take are some prefix and some suffix; equivalently the cards you
leave behind form one contiguous window of length `len(cardPoints) - k`, so the
score equals the total minus the minimum such window.

**Examples**
```
cardPoints = [1,2,3,4,5,6,1], k = 3  ->  12   (take 1 + 6 + 5 from the right)
cardPoints = [2,2,2], k = 2          ->  4
cardPoints = [9,7,7,9,7,7,9], k = 7  ->  55   (take every card)
```

**Constraints:** `1 <= len(cardPoints) <= 10^5`, `1 <= cardPoints[i] <= 10^4`,
`1 <= k <= len(cardPoints)`.
