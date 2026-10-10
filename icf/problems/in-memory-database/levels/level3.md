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

should insert a field-value pair, or update the value of the field, in the
record associated with `key`, and set its Time-To-Live to `ttl` starting at
`timestamp`. The `ttl` is the amount of time that this field-value pair should
exist in the database, meaning it is available during the interval
`[timestamp, timestamp + ttl)`: it can be read at any timestamp up to, but not
including, `timestamp + ttl`, and at exactly `timestamp + ttl` it has expired.
A `ttl` of `0` means the field is already expired. Returns nothing.

### How the existing operations change

- All operations treat an expired field as if it doesn't exist: `get` returns
  `None`, `delete` returns `False`, `compare_and_set` returns `False`, and
  neither `scan` nor `scan_by_prefix` lists it.
- Whether a field has expired depends on the timestamp of the call that looks
  at it — not on the moment it was written.
- Fields written without a TTL never expire.
- If `set_with_ttl` is called for a field that already exists, both its value
  and its lifetime are replaced: the countdown starts again from the new
  `timestamp`, and the new lifetime may be longer or shorter than the old one.
- A plain `set` on a field removes its lifetime, so the field becomes
  permanent again.
- `compare_and_set` keeps the field's current lifetime: it changes the value,
  but does not extend, shorten or remove the countdown.
- An expired field can be written again with `set` or `set_with_ttl`, exactly
  like a field that never existed. A record whose fields have all expired
  scans as `""`, but still accepts new writes.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set_with_ttl(1, "session", "token", "abc", 9)` | database state: `{"session": {"token": "abc"}}`, where `token` expires at timestamp 10 |
| `db.set(2, "session", "user", "ada")` | database state: `{"session": {"token": "abc", "user": "ada"}}`, where `user` does not expire |
| `db.get(9, "session", "token")` | returns `"abc"`; timestamp 9 is still inside `[1, 10)` |
| `db.get(10, "session", "token")` | returns `None`; the field expired at exactly 1 + 9 = 10 |
| `db.scan(11, "session")` | returns `"user(ada)"`; the expired field is not listed |
| `db.delete(12, "session", "token")` | returns `False`; an expired field can't be deleted |
| `db.set_with_ttl(13, "session", "token", "def", 5)` | database state: `{"session": {"token": "def", "user": "ada"}}`, where `token` expires at timestamp 18 |
| `db.set_with_ttl(15, "session", "token", "ghi", 10)` | the field already exists, so the countdown restarts; `token` now expires at timestamp 25 |
| `db.compare_and_set(24, "session", "token", "ghi", "jkl")` | returns `True`; the value changes, but `token` still expires at timestamp 25 |
| `db.get(25, "session", "token")` | returns `None`; the field has expired |
| `db.set_with_ttl(26, "session", "token", "mno", 3)` | `token` expires at timestamp 29 |
| `db.set(27, "session", "token", "pqr")` | a plain `set` removes the lifetime, so `token` does not expire |
| `db.get(1000, "session", "token")` | returns `"pqr"` |
