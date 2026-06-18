There are `2n` distinguishable balls in `k` colors; `balls[i]` of them are color `i`
(`sum(balls)` is even). After a uniformly random shuffle, the first `n` balls go to
box 1 and the rest to box 2. **Return the probability that the two boxes contain the
same number of distinct colors** (answers within `1e-5` are accepted; this judge
expects the value rounded to 5 decimals).

**Examples**
```
balls = [1,1]          ->  1.00000
balls = [2,1,1]        ->  0.66667
balls = [1,2,1,2]      ->  0.60000
balls = [3,2,1]        ->  0.30000
balls = [6,6,6,6,6,6]  ->  0.90327
```

**Constraints:** `1 <= len(balls) <= 8`, `1 <= balls[i] <= 6`, `sum(balls)` even.
