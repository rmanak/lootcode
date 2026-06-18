Alice starts with `0` points and repeatedly draws while she has fewer than `K`
points; each draw adds a uniformly random integer in `[1, W]`. She stops once she has
`K` or more points. **Return the probability that her final score is `<= N`, rounded
to 5 decimal places.** (Answers within `1e-5` are accepted.)

**Examples**
```
N = 10, K = 1, W = 10  ->  1.00000
N = 6, K = 1, W = 10   ->  0.60000
N = 21, K = 17, W = 10 ->  0.73278
```

**Constraints:** `0 <= K <= N <= 10^4`, `1 <= W <= 10^4`.
