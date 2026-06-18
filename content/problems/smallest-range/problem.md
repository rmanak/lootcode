You have `k` lists of integers, each sorted in non-decreasing order. Find the smallest
range `[a, b]` that includes **at least one** number from each of the `k` lists.
Range `[a, b]` is smaller than `[c, d]` if `b - a < d - c`, or `b - a == d - c` and
`a < c`. Return the range as `[a, b]`.

**Example**
```
nums = [[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]   ->  [20,24]
```

**Constraints:** `1 <= k`; each list is non-decreasing; values fit in `int`.
