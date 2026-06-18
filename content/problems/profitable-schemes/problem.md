A gang of `n` members can commit a list of crimes. Crime `i` needs `group[i]`
members and yields `profit[i]`. A member who joins one crime cannot join another,
so a chosen subset of crimes uses `sum(group[i])` members in total.

A subset is **profitable** if it earns at least `minProfit` profit using at most
`n` members. **Return the number of profitable subsets**, modulo `10^9 + 7`.

**Examples**
```
n = 5,  minProfit = 3, group = [2,2],   profit = [2,3]  ->  2
n = 10, minProfit = 5, group = [2,3,5], profit = [6,7,8] ->  7
```

**Constraints:** `1 <= n <= 100`, `0 <= minProfit <= 100`,
`1 <= len(group) == len(profit) <= 100`, `1 <= group[i] <= 100`,
`0 <= profit[i] <= 100`.
