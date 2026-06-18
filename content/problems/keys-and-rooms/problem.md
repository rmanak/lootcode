There are `N` rooms numbered `0..N-1`; you start in room `0`, which is unlocked, and
all others are locked. Room `i` contains the keys `rooms[i]`, and a key with value
`v` unlocks room `v`. You may move freely between unlocked rooms. Return `True` if
you can unlock and enter **every** room.

**Examples**
```
rooms = [[1],[2],[3],[]]          ->  True
rooms = [[1,3],[3,0,1],[2],[0]]   ->  False
```

**Constraints:** `1 <= len(rooms) <= 1000`, `0 <= len(rooms[i]) <= 1000`, total keys
`<= 3000`.
