In the grid, `.` is empty, `#` is a wall, `@` is the start, lowercase letters are
keys and uppercase letters are locks. You move in the 4 directions, picking up keys
you step on; you may enter a lock only if you already hold its key. **Return the
fewest moves to collect every key, or `-1` if impossible.**

**Examples**
```
["@.a.#","###.#","b.A.B"]  ->  8
["@..aA","..B#.","....b"]   ->  6
```

**Constraints:** `1 <= rows, cols <= 30`; there is exactly one `@`; the keys are the
first `k` letters of `a..f` (`1 <= k <= 6`), each appearing exactly once; each lock
appears at most once, and only if its key is in the grid.
