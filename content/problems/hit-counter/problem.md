Design a hit counter which counts the number of hits received in the past
`5` minutes (i.e. the past `300` seconds).

Your system should accept a `timestamp` parameter (**in seconds** granularity),
and you may assume that calls are being made to the system in chronological order
(i.e. `timestamp` is monotonically non-decreasing). Several hits may arrive at
roughly the same time.

Implement the `HitCounter` class:

- `HitCounter()` initializes the object of the hit counter system.
- `void hit(int timestamp)` records a hit that happened at `timestamp` (in
  seconds). Several hits may happen at the same `timestamp`.
- `int getHits(int timestamp)` returns the number of hits in the past 5 minutes
  from `timestamp` (i.e. the past `300` seconds), that is hits whose timestamp
  lies in `(timestamp - 300, timestamp]`.

**Example 1:**

```
Input
["HitCounter", "hit", "hit", "hit", "getHits", "hit", "getHits", "getHits"]
[[], [1], [2], [3], [4], [300], [300], [301]]

Output
[null, null, null, null, 3, null, 4, 3]
```

Explanation: the three hits at `1`, `2`, `3` are all within 300 seconds of `4`.
At `timestamp = 300` the hit at `300` is counted as well, but by `timestamp = 301`
the hit at `1` has aged out of the window.

**Example 2:**

```
Input
["HitCounter", "hit", "getHits"]
[[], [1], [1]]

Output
[null, null, 1]
```

**Constraints:**

- `1 <= timestamp <= 2 * 10⁹`
- All calls are made with non-decreasing values of `timestamp`.
- At most `10⁵` calls will be made to `hit` and `getHits`.
