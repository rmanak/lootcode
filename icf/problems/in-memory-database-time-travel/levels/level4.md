When something goes wrong, an operator wants to know what the configuration
looked like at the moment it happened. Introduce an operation that reads the
value a field held at any earlier moment, taking every write, delete and
expiry into account.

```python
get_when(self, timestamp: int, key: str, field: str, at_timestamp: int) -> str | None
```

should return the value that `field` of the record associated with `key` held
at the moment `at_timestamp` — that is, the value a `get` call made at
`at_timestamp` would have returned. It is guaranteed that `at_timestamp` is
never later than `timestamp`. Specifically:

- A write made at exactly `at_timestamp` counts: the result reflects the state
  after that write.
- Returns `None` if the field had never been written by `at_timestamp`, or if
  the record doesn't exist.
- Returns `None` if the field had been deleted by `at_timestamp` and not
  written again since.
- Returns `None` if the field's value had expired by `at_timestamp`: a value
  written with a lifetime ending at `T` is visible for every `at_timestamp`
  before `T` and not from `T` on.
- A deleted or expired value never "falls back" to an older one: if a field
  held `"a"`, was then overwritten with `"b"` and `"b"` expired, the field had
  no value from that moment, not `"a"`.
- Only successful writes change history. A `compare_and_set`,
  `compare_and_set_with_ttl` or `compare_and_delete` that returned `False`
  left no trace.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set(1, "cfg", "mode", "safe")` |  |
| `db.set(5, "cfg", "mode", "fast")` |  |
| `db.set_with_ttl(8, "cfg", "mode", "turbo", 4)` | `"turbo"` is alive on `[8, 12)` |
| `db.compare_and_delete(15, "cfg", "mode", "turbo")` | returns `False`; the field had already expired at 12 |
| `db.set(20, "cfg", "mode", "eco")` |  |
| `db.compare_and_delete(25, "cfg", "mode", "eco")` | returns `True` |
| `db.get_when(30, "cfg", "mode", 0)` | returns `None`; nothing had been written yet |
| `db.get_when(31, "cfg", "mode", 4)` | returns `"safe"` |
| `db.get_when(32, "cfg", "mode", 5)` | returns `"fast"`; the write at exactly `at_timestamp` counts |
| `db.get_when(33, "cfg", "mode", 11)` | returns `"turbo"` |
| `db.get_when(34, "cfg", "mode", 12)` | returns `None`; the TTL ran out at 12; the field does not fall back to `"fast"` |
| `db.get_when(35, "cfg", "mode", 20)` | returns `"eco"` |
| `db.get_when(36, "cfg", "mode", 25)` | returns `None`; the field was deleted at 25 |
| `db.get_when(37, "cfg", "speed", 20)` | returns `None`; the field never existed |
