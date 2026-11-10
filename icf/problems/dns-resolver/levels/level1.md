Initially, the zone is empty, so implement operations to add and remove
**address records** — each one says that a name can be reached at an IP
address — and to resolve a name to its addresses. A name may have several
addresses, for example when a site runs on more than one server.

```python
add_record(self, timestamp: int, name: str, ip: str) -> bool
```

should add an address record mapping `name` to `ip`. Returns `True` if the
record was added, or `False` if `name` already has the address `ip` — in which
case nothing changes. Different names may share an address.

```python
remove_record(self, timestamp: int, name: str, ip: str) -> bool
```

should remove the address `ip` from `name`. Returns `True` if it was removed,
or `False` if `name` doesn't have that address.

```python
resolve(self, timestamp: int, name: str) -> list[str] | None
```

should return the addresses of `name`, in the order they were added. Returns
`None` if the name has no addresses. An address that was removed and then
added again counts as newly added, so it goes to the end of the list.

Remember that names are normalized (see the overview): every operation here
treats `"Example.com."` and `"example.com"` as the same name.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `dns = Resolver()` | an empty zone |
| `dns.add_record(1, "Example.com.", "93.184.216.34")` | returns `True`; stored under the name `"example.com"` |
| `dns.add_record(2, "example.com", "93.184.216.35")` | returns `True` |
| `dns.add_record(3, "EXAMPLE.COM", "93.184.216.34")` | returns `False`; the same name already has this address |
| `dns.resolve(4, "example.com.")` | returns `["93.184.216.34", "93.184.216.35"]`; addresses in the order they were added |
| `dns.resolve(5, "example.org")` | returns `None`; no records for this name |
| `dns.remove_record(6, "example.com", "93.184.216.34")` | returns `True` |
| `dns.remove_record(7, "example.com", "93.184.216.34")` | returns `False`; already removed |
| `dns.resolve(8, "example.com")` | returns `["93.184.216.35"]` |
| `dns.add_record(9, "example.com", "93.184.216.34")` | returns `True`; a re-added address goes to the end |
| `dns.resolve(10, "example.com")` | returns `["93.184.216.35", "93.184.216.34"]` |
