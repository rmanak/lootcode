`prices[i]` is the stock price on day `i`. You may complete any number of
transactions but must sell before buying again, and after selling you must wait one
day (cooldown) before buying. **Return the maximum profit.**

**Example**
```
prices = [1,2,3,0,2]  ->  3    (buy, sell, cooldown, buy, sell)
```

**Constraints:** `0 <= len(prices) <= 5000`, `0 <= prices[i] <= 1000`.
