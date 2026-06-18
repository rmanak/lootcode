Job `i` has difficulty `difficulty[i]` and pays `profit[i]`. Worker `j` can do any
single job with difficulty at most `worker[j]` (a job may be done by many workers).
**Return the maximum total profit.** A worker who cannot do any job earns `0`.

**Example**
```
difficulty = [2,4,6,8,10], profit = [10,20,30,40,50], worker = [4,5,6,7]  ->  100
```

**Constraints:** `1 <= len(difficulty) == len(profit) <= 10^4`,
`1 <= len(worker) <= 10^4`, all values in `[1, 10^5]`.
