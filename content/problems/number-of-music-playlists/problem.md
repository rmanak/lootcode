Your music player has `n` different songs and you want to listen to `goal` songs
(repeats allowed) during a trip. Build a playlist so that:

- every one of the `n` songs is played **at least once**, and
- a song can be replayed only after at least `k` **other** songs have been played
  since its previous play.

**Return the number of possible playlists**, modulo `10^9 + 7`.

**Examples**
```
n = 3, goal = 3, k = 1  ->  6
n = 2, goal = 3, k = 0  ->  6
n = 2, goal = 3, k = 1  ->  2   (only [1,2,1] and [2,1,2])
```

**Constraints:** `0 <= k < n <= goal <= 100`.
