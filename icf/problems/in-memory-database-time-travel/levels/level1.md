The basic level of the in-memory database contains records, so implement
operations to write a field and read it back. Because several clients share
the database, a field is updated or removed only on condition that it still
holds the value the client expects — if someone else changed it in the
meantime, the operation does nothing and reports that it failed.

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
compare_and_set(self, timestamp: int, key: str, field: str, expected_value: str, new_value: str) -> bool
```

should replace the value of `field` in the record associated with `key` with
`new_value`, but only if the field currently holds exactly `expected_value` —
a case-sensitive, character-for-character match. Returns `True` if the value
was replaced, and `False` otherwise, in which case nothing changes.
Specifically:

- Returns `False` if the record or the field doesn't exist. Unlike `set`,
  `compare_and_set` never creates a missing record or field.
- Returns `False` if the field holds a value other than `expected_value`.
- Returns `True` if the field holds `expected_value`, even when `new_value` is
  the same as the value already stored.

```python
compare_and_delete(self, timestamp: int, key: str, field: str, expected_value: str) -> bool
```

should remove `field` from the record associated with `key`, but only if the
field currently holds exactly `expected_value`. Returns `True` if the field was
deleted, and `False` otherwise, in which case nothing changes. It returns
`False` if the record or the field doesn't exist, or if the field holds a
value other than `expected_value`. A deleted field can be written again with
`set`, exactly like a field that never existed.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set(1, "user1", "role", "reader")` | database state: `{"user1": {"role": "reader"}}` |
| `db.set(2, "user1", "name", "Ada")` | database state: `{"user1": {"role": "reader", "name": "Ada"}}` |
| `db.get(3, "user1", "role")` | returns `"reader"` |
| `db.get(4, "user2", "role")` | returns `None`; there is no record `user2` |
| `db.compare_and_set(5, "user1", "role", "reader", "admin")` | returns `True`; the field held `"reader"`; database state: `{"user1": {"role": "admin", "name": "Ada"}}` |
| `db.compare_and_set(6, "user1", "role", "reader", "owner")` | returns `False`; the field holds `"admin"` now, so nothing changes |
| `db.compare_and_set(7, "user1", "email", "", "a@b.c")` | returns `False`; the field `email` doesn't exist, and it is not created |
| `db.compare_and_delete(8, "user1", "name", "Grace")` | returns `False`; the field holds `"Ada"`, so it is not deleted |
| `db.compare_and_delete(9, "user1", "name", "Ada")` | returns `True`; database state: `{"user1": {"role": "admin"}}` |
| `db.get(10, "user1", "name")` | returns `None`; the field was deleted |
