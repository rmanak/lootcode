Support the timeline of operations and TTL (Time-To-Live) settings for fields.
Some data should not live forever — a login session or a cached value is only
valid for a while — so a field can now be written with a lifetime, after which
the database behaves as if the field had been deleted.

Every operation already receives the `timestamp` at which it is executed. From
this level on it matters: a call made at `timestamp` must only see the fields
that are still alive at that moment.

```python
set_with_ttl(self, timestamp: int, key: str, field: str, value: str, ttl: int) -> None
```

should insert a field-value pair, or replace the value of the field, in the
record associated with `key`, and give it a lifetime of `ttl` starting at
`timestamp`. The field is then available during the interval
`[timestamp, timestamp + ttl)`: it can be read at any timestamp up to, but not
including, `timestamp + ttl`, and at exactly `timestamp + ttl` it has expired.
A `ttl` of `0` means the field is already expired. Returns nothing.

```python
compare_and_set_with_ttl(self, timestamp: int, key: str, field: str, expected_value: str, new_value: str, ttl: int) -> bool
```

works exactly like `compare_and_set` — same conditions, same `True`/`False` —
but when it succeeds it also gives the field a new lifetime of `ttl` starting
at `timestamp`, replacing whatever lifetime the field had before (or making a
permanent field expire).

### How the existing operations change

- All operations treat an expired field as if it doesn't exist: `get` returns
  `None`, `compare_and_set`, `compare_and_set_with_ttl` and
  `compare_and_delete` return `False`, and neither `scan` nor `scan_by_prefix`
  lists it.
- Whether a field has expired depends on the timestamp of the call that looks
  at it — not on the moment it was written.
- Fields written without a TTL never expire.
- `set_with_ttl` on a field that already exists replaces both its value and
  its lifetime: the countdown starts again from the new `timestamp`, and may
  be longer or shorter than before.
- A plain `set` on a field removes its lifetime, so the field becomes
  permanent again.
- `compare_and_set` keeps the field's current lifetime: it changes the value,
  but does not extend, shorten or remove the countdown.
- An expired field can be written again with `set` or `set_with_ttl`, exactly
  like a field that never existed.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set_with_ttl(1, "session", "token", "abc", 9)` | `token` is alive on `[1, 10)` |
| `db.set(2, "session", "user", "ada")` | `user` never expires |
| `db.get(9, "session", "token")` | returns `"abc"`; timestamp 9 is still inside `[1, 10)` |
| `db.scan(10, "session")` | returns `["user(ada)"]`; the token expired at exactly 1 + 9 = 10 |
| `db.compare_and_delete(11, "session", "token", "abc")` | returns `False`; an expired field can't be compared |
| `db.set_with_ttl(12, "session", "token", "def", 10)` | `token` is alive on `[12, 22)` |
| `db.compare_and_set(15, "session", "token", "def", "ghi")` | returns `True`; the value changes, but `token` still expires at 22 |
| `db.get(22, "session", "token")` | returns `None` |
| `db.set(23, "session", "token", "jkl")` | `token` is written again, without a lifetime |
| `db.compare_and_set_with_ttl(24, "session", "token", "jkl", "mno", 5)` | returns `True`; the new value is alive on `[24, 29)` |
| `db.scan_by_prefix(28, "session", "t")` | returns `["token(mno)"]` |
| `db.scan_by_prefix(29, "session", "t")` | returns `[]` |
