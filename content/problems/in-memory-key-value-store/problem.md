Design an in-memory key-value store that supports **snapshots**: a snapshot
captures the contents at that moment and can be read from afterwards, even after
later writes and deletes.

Implement the `KeyValueStore` class:

- `KeyValueStore()` initializes an empty store with no snapshots.
- `void set(String key, int value)` sets `key` to `value` in the current contents.
- `int get(String key)` returns the current value of `key`, or `null` if `key` is
  absent.
- `void delete(String key)` removes `key` from the current contents. Deleting an
  absent key is a no-op.
- `int snapshot()` captures the current contents and returns its version id.
  Version ids are assigned in increasing order starting from `0`.
- `int getAt(String key, int id)` returns the value of `key` as of snapshot `id`,
  or `null` if `key` was absent in that snapshot or `id` is not a valid version.

**Example 1:**

```
Input
["KeyValueStore", "set", "snapshot", "set", "get", "getAt", "delete", "get"]
[[], ["a", 1], [], ["a", 2], ["a"], ["a", 0], ["a"], ["a"]]

Output
[null, null, 0, null, 2, 1, null, null]
```

Explanation: the snapshot keeps `a = 1` readable through `getAt("a", 0)` even after
`set("a", 2)` and the later `delete("a")`.

**Example 2:**

```
Input
["KeyValueStore", "get"]
[[], ["x"]]

Output
[null, null]
```

Explanation: reading an absent key gives `null`.

**Constraints:**

- Keys are non-empty strings; `-10⁹ <= value <= 10⁹`.
- At most `10⁵` calls will be made across all methods.
