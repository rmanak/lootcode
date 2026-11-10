Many names are just other names in disguise — `www.example.com` is often the
same site as `example.com`. Implement **aliases** (CNAME records, in DNS
terms): a name that points at a target name, so that resolving the alias
resolves the target instead.

```python
add_alias(self, timestamp: int, name: str, target: str) -> bool
```

should make `name` an alias for `target`. The target does not need to exist
yet. Returns `True` if the alias was added, or `False` otherwise, in which case
nothing changes. Specifically:

- Returns `False` if `name` and `target` are the same name.
- Returns `False` if `name` is already an alias. A name has at most one alias.
- Returns `False` if `name` has address records. A name is **either** an alias
  **or** a name with addresses, never both.

```python
remove_alias(self, timestamp: int, name: str) -> bool
```

should remove the alias of `name`. Returns `True` if it was removed, or `False`
if `name` is not an alias. Afterwards the name is free: it may be given
addresses or a new alias.

```python
get_chain(self, timestamp: int, name: str) -> list[str]
```

should return the names visited when following aliases from `name`: the
normalized `name` itself first, then its target, then the target's target,
and so on, ending with the first name that is not an alias. If following the
aliases would visit a name a second time, the chain is a **loop**: the list
ends with that repeated name, appearing a second time, and goes no further. A
name that is not an alias has the chain `[name]`.

How the existing operations change:

- `resolve` follows the chain of aliases from `name` and returns the addresses
  of the name at the end of it. It returns `None` if that name has no
  addresses (a dead end), or if the chain is a loop.
- `add_record` returns `False` if `name` is an alias.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `dns = Resolver()` | an empty zone |
| `dns.add_record(1, "web.example.net", "10.0.0.7")` | returns `True` |
| `dns.add_alias(2, "www.example.com", "web.example.net")` | returns `True` |
| `dns.add_alias(3, "shop.example.com", "WWW.example.com.")` | returns `True`; the target is normalized too |
| `dns.resolve(4, "shop.example.com")` | returns `["10.0.0.7"]`; shop → www → web, which has an address |
| `dns.get_chain(5, "shop.example.com")` | returns `["shop.example.com", "www.example.com", "web.example.net"]` |
| `dns.add_alias(6, "shop.example.com", "web.example.net")` | returns `False`; the name already is an alias |
| `dns.add_record(7, "www.example.com", "10.0.0.8")` | returns `False`; an alias cannot also have addresses |
| `dns.add_alias(8, "web.example.net", "cdn.example.net")` | returns `False`; a name with addresses cannot become an alias |
| `dns.add_alias(9, "a.test", "b.test")` | returns `True` |
| `dns.add_alias(10, "b.test", "a.test")` | returns `True` |
| `dns.resolve(11, "a.test")` | returns `None`; the chain loops |
| `dns.get_chain(12, "a.test")` | returns `["a.test", "b.test", "a.test"]`; the chain stops at the first repeated name |
| `dns.remove_alias(13, "b.test")` | returns `True` |
| `dns.get_chain(14, "a.test")` | returns `["a.test", "b.test"]`; b.test is no longer an alias, and it has no addresses |
| `dns.resolve(15, "a.test")` | returns `None` |
