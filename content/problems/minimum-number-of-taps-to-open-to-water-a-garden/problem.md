A garden spans `[0, n]` with a tap at each integer point `0..n`. Tap `i` waters
`[i - ranges[i], i + ranges[i]]`. **Return the minimum number of taps to water the
whole garden**, or `-1` if impossible.

**Examples**
```
n = 5, ranges = [3,4,1,1,0,0]      ->  1
n = 3, ranges = [0,0,0,0]          ->  -1
n = 7, ranges = [1,2,1,0,2,1,0,1]  ->  3
```

**Constraints:** `1 <= n <= 10^4`, `len(ranges) == n+1`, `0 <= ranges[i] <= 100`.
