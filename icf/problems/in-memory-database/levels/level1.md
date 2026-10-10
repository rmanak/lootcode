The basic level of the in-memory database contains records, so implement
operations to write a field, read it back, remove it, and update it only if it
still holds the value you expect.

```python
set(self, timestamp: int, key: str, field: str, value: str) -> None
```

should insert a field-value pair into the record associated with `key`. If the
field already exists in the record, replace its value with `value`. If the
record does not exist, create a new one. Returns nothing.

```python
get(self, timestamp: int, key: str, field: str) -> str | None
```

should return the value contained within `field` of the record associated with
`key`. Returns `None` if the record or the field doesn't exist.

```python
delete(self, timestamp: int, key: str, field: str) -> bool
```

should remove `field` from the record associated with `key`. Returns `True` if
the field was successfully deleted, and `False` if the record or the field
doesn't exist. Deleting the last field of a record is allowed: the record is
then simply empty, and new fields can still be written to it.

```python
compare_and_set(self, timestamp: int, key: str, field: str, expected: str, new_value: str) -> bool
```

should replace the value of `field` in the record associated with `key` with
`new_value`, but only if the field currently holds exactly `expected` — a
case-sensitive, character-for-character match. This is how a client safely
updates a value that someone else might have changed in the meantime. Returns
`True` if the value was replaced, and `False` otherwise, in which case nothing
changes. Specifically:

- Returns `False` if the record or the field doesn't exist. Unlike `set`,
  `compare_and_set` never creates a missing record or field.
- Returns `False` if the field holds a value other than `expected`.
- Returns `True` if the field holds `expected`, even when `new_value` is the
  same as the value already stored.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set(1, "user1", "name", "Ada")` | database state: `{"user1": {"name": "Ada"}}` |
| `db.set(2, "user1", "role", "reader")` | database state: `{"user1": {"name": "Ada", "role": "reader"}}` |
| `db.set(3, "user2", "name", "Grace")` | database state: `{"user1": {"name": "Ada", "role": "reader"}, "user2": {"name": "Grace"}}` |
| `db.get(4, "user1", "name")` | returns `"Ada"` |
| `db.get(5, "user1", "email")` | returns `None`; record `user1` has no field `email` |
| `db.get(6, "user3", "name")` | returns `None`; there is no record `user3` |
| `db.set(7, "user1", "name", "Ada L.")` | the field already exists, so its value is replaced; database state: `{"user1": {"name": "Ada L.", "role": "reader"}, "user2": {"name": "Grace"}}` |
| `db.compare_and_set(8, "user1", "role", "reader", "admin")` | returns `True`; the field held `"reader"`; database state: `{"user1": {"name": "Ada L.", "role": "admin"}, "user2": {"name": "Grace"}}` |
| `db.compare_and_set(9, "user1", "role", "reader", "owner")` | returns `False`; the field holds `"admin"` now, so nothing changes |
| `db.compare_and_set(10, "user1", "email", "x", "a@b.c")` | returns `False`; the field `email` doesn't exist, and it is not created |
| `db.delete(11, "user1", "role")` | returns `True`; database state: `{"user1": {"name": "Ada L."}, "user2": {"name": "Grace"}}` |
| `db.delete(12, "user1", "role")` | returns `False`; the field was already deleted |
