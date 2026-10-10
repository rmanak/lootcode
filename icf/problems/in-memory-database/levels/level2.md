The database should support displaying data based on filters, so introduce
operations to list the fields of a record — all of them, or only those whose
names start with a given prefix. This is what an admin console uses to show a
whole record at a glance instead of reading it one field at a time.

```python
scan(self, timestamp: int, key: str) -> str
```

should return a single string listing every field of the record associated
with `key`, in the following format:

```
"<field_1>(<value_1>), <field_2>(<value_2>), ..., <field_n>(<value_n>)"
```

where fields are sorted lexicographically by name and separated by a comma and
one space. Values are written exactly as they are stored. Returns an empty
string `""` if the record doesn't exist or has no fields.

```python
scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> str
```

should return a string listing only the fields of the record associated with
`key` whose names start with `prefix`. The format, the sort order and the
empty-result rule are the same as in `scan`, so it returns `""` if no field
matches. The empty prefix matches every field, and a prefix equal to a whole
field name matches that field.

"Lexicographically" means ordinary Python string comparison (`<` on `str`):
uppercase letters sort before lowercase ones (`"Zebra"` before `"apple"`), and
digits are compared character by character (`"10"` before `"9"`).

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set(1, "cfg", "db_port", "5432")` | database state: `{"cfg": {"db_port": "5432"}}` |
| `db.set(2, "cfg", "db_host", "10.0.0.4")` | database state: `{"cfg": {"db_port": "5432", "db_host": "10.0.0.4"}}` |
| `db.set(3, "cfg", "region", "eu")` | database state: `{"cfg": {"db_port": "5432", "db_host": "10.0.0.4", "region": "eu"}}` |
| `db.scan_by_prefix(4, "cfg", "db_")` | returns `"db_host(10.0.0.4), db_port(5432)"`; fields are sorted by name, not by when they were written |
| `db.scan(5, "cfg")` | returns `"db_host(10.0.0.4), db_port(5432), region(eu)"` |
| `db.scan_by_prefix(6, "cfg", "cache")` | returns `""`; no field starts with `cache` |
| `db.scan(7, "other")` | returns `""`; there is no record `other` |
| `db.delete(8, "cfg", "region")` | returns `True` |
| `db.scan(9, "cfg")` | returns `"db_host(10.0.0.4), db_port(5432)"`; the deleted field is gone |
