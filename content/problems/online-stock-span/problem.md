Given the daily stock `prices` in order, return the list of **spans**. The span on a
day is the number of consecutive days ending on that day (going backwards) for which
the price was less than or equal to that day's price.

**Example**
```
prices = [100,80,60,70,60,75,85]   ->  [1,1,1,2,1,4,6]
```

**Constraints:** `1 <= len(prices) <= 10^4`, `1 <= prices[i] <= 10^5`.
