Video clips cover a sporting event lasting `T` seconds. Clip `clips[i] = [a, b]`
covers the interval `[a, b]` and may be cut freely. Return the minimum number of
clips needed to cover `[0, T]` entirely, or `-1` if it is impossible.

**Examples**
```
clips = [[0,2],[4,6],[8,10],[1,9],[1,5],[5,9]], T = 10   ->  3
clips = [[0,1],[1,2]], T = 5                              ->  -1
clips = [[0,4],[2,8]], T = 5                              ->  2
```

**Constraints:** `1 <= len(clips) <= 100`, `0 <= a <= b <= 100`, `0 <= T <= 100`.
