Design a simplified **consistent-hash ring**. Integer server ids sit on a ring at
their own value, and a key is served by the first server found walking
**clockwise** (i.e. the smallest server id `>= key`, wrapping around to the
smallest id of all if none qualifies).

Implement the `HashRing` class:

- `HashRing()` initializes an empty ring.
- `void addServer(int id)` puts the server `id` on the ring. Adding an id that is
  already present is a no-op.
- `void removeServer(int id)` takes the server `id` off the ring. Removing an
  absent id is a no-op.
- `int getServer(int key)` returns the id of the first server clockwise from
  `key`, or `null` if the ring has no servers.

**Example 1:**

```
Input
["HashRing", "addServer", "addServer", "addServer", "getServer", "getServer", "getServer", "getServer", "removeServer", "getServer"]
[[], [10], [20], [30], [5], [15], [25], [35], [20], [15]]

Output
[null, null, null, null, 10, 20, 30, 10, null, 30]
```

Explanation: with servers `{10, 20, 30}`, key `5` maps to `10` and key `35` wraps
around to `10`. After `removeServer(20)`, key `15` maps to `30`.

**Example 2:**

```
Input
["HashRing", "getServer"]
[[], [1]]

Output
[null, null]
```

Explanation: an empty ring serves nothing.

**Constraints:**

- `0 <= id, key <= 10⁹`
- At most `10⁵` calls will be made to `addServer`, `removeServer`, and `getServer`.
