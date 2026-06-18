Over `n` minutes, `customers[i]` customers arrive in minute `i` and leave at its
end. If `grumpy[i] == 1` they are unsatisfied that minute. The owner can suppress
grumpiness for one window of `X` consecutive minutes. **Return the maximum number of
satisfied customers.**

**Example**
```
customers = [1,0,1,2,1,1,7,5], grumpy = [0,1,0,1,0,1,0,1], X = 3  ->  16
```

**Constraints:** `1 <= X <= len(customers) <= 2*10^4`, `0 <= customers[i] <= 1000`,
`grumpy[i]` in `{0,1}`.
