The database should support displaying data based on filters, so introduce
operations to list the fields of a record — all of them, or only those whose
names start with a given prefix. This is what an admin console uses to show a
whole record at a glance instead of reading it one field at a time.

```python
scan(self, timestamp: int, key: str) -> list[str]
```

should return a list of strings describing every field of the record
associated with `key`, in the following format:

```
["<field_1>(<value_1>)", "<field_2>(<value_2>)", ..., "<field_n>(<value_n>)"]
```

where fields are sorted lexicographically by name. Values are written exactly
as they are stored, so an empty value appears as `"<field>()"`. Returns an
empty list if the record doesn't exist or has no fields.

```python
scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> list[str]
```

should return the same kind of list, but only for the fields of the record
associated with `key` whose names start with `prefix`. The format, the sort
order and the empty-result rule are the same as in `scan`. The empty prefix
matches every field, a prefix equal to a whole field name matches that field,
and matching is case-sensitive.

"Lexicographically" means ordinary Python string comparison (`<` on `str`):
uppercase letters sort before lowercase ones (`"Zebra"` before `"apple"`), and
digits are compared character by character (`"10"` before `"9"`).

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set(1, "cfg", "db_port", "5432")` |  |
| `db.set(2, "cfg", "db_host", "10.0.0.4")` |  |
| `db.set(3, "cfg", "region", "eu")` | database state: `{"cfg": {"db_port": "5432", "db_host": "10.0.0.4", "region": "eu"}}` |
| `db.scan(4, "cfg")` | returns `["db_host(10.0.0.4)", "db_port(5432)", "region(eu)"]`; fields are sorted by name, not by when they were written |
| `db.scan_by_prefix(5, "cfg", "db_")` | returns `["db_host(10.0.0.4)", "db_port(5432)"]` |
| `db.scan_by_prefix(6, "cfg", "cache")` | returns `[]`; no field starts with `cache` |
| `db.compare_and_delete(7, "cfg", "region", "eu")` | returns `True` |
| `db.scan(8, "cfg")` | returns `["db_host(10.0.0.4)", "db_port(5432)"]`; the deleted field is gone |
| `db.scan(9, "other")` | returns `[]`; there is no record `other` |
