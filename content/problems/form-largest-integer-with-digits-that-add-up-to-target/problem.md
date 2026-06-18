`cost[i]` is the cost to paint the digit `i+1` (digits `1`..`9`, no `0`). Spending
**exactly** `target` total cost, **return the largest integer you can paint** as a
string, or `"0"` if it is impossible.

**Examples**
```
cost = [4,3,2,5,6,7,2,5,5], target = 9   ->  "7772"
cost = [7,6,5,5,5,6,8,7,8], target = 12  ->  "85"
cost = [2,4,6,2,4,6,4,4,4], target = 5   ->  "0"
```

**Constraints:** `len(cost) == 9`, `1 <= cost[i] <= 5000`, `1 <= target <= 5000`.
