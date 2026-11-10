Real DNS records come with a **TTL** (Time-To-Live): how long the record may be
relied on. Support records that expire, and tell clients how long an answer
stays valid, so that they know when to ask again.

```python
add_record_with_ttl(self, timestamp: int, name: str, ip: str, ttl: int) -> bool
```

should behave like `add_record`, but the record only exists during the
interval `[timestamp, timestamp + ttl)`: it is there at every timestamp up to,
but not including, `timestamp + ttl`, and at exactly `timestamp + ttl` it has
expired. A `ttl` of `0` means the record is already expired.

```python
add_alias_with_ttl(self, timestamp: int, name: str, target: str, ttl: int) -> bool
```

should behave like `add_alias`, but the alias only exists during the interval
`[timestamp, timestamp + ttl)`.

```python
get_answer_ttl(self, timestamp: int, name: str) -> int | None
```

should resolve `name` at `timestamp` and return how many milliseconds the
answer remains valid. Returns `None` if the outcome is not `"RESOLVED"`.
Otherwise, the answer relied on these records:

- every alias followed along the chain that produced the answer — for an
  answer that came from a fallback, the fallback's own chain, not the dead-end
  chain that led to trying it;
- every address record returned.

The result is the smallest remaining lifetime among them, where a record that
expires at `T` has `T - timestamp` left. If none of those records expires,
returns `-1`.

### How the existing operations change

- An expired record behaves exactly as if it had been removed, in every
  operation: `resolve`, `get_chain` and `get_status` don't see it,
  `remove_record` and `remove_alias` return `False` for it, and it no longer
  blocks `add_record`, `add_alias` or their TTL versions.
- An expired address can be added again; it counts as newly added, so it goes
  to the end of the name's list of addresses.
- The rule that a name is either an alias or has addresses applies to records
  that are alive at the same moment. A name whose alias has expired may be
  given addresses, and the other way around.
- Records added with `add_record` and `add_alias` never expire.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `dns = Resolver()` | an empty zone |
| `dns.add_record_with_ttl(1000, "origin.net", "10.0.0.1", 60000)` | returns `True`; alive on `[1000, 61000)` |
| `dns.add_record(2000, "origin.net", "10.0.0.2")` | returns `True`; never expires |
| `dns.add_alias_with_ttl(3000, "www.site.com", "origin.net", 30000)` | returns `True`; alive on `[3000, 33000)` |
| `dns.resolve(9000, "www.site.com")` | returns `["10.0.0.1", "10.0.0.2"]` |
| `dns.get_answer_ttl(10000, "www.site.com")` | returns `23000`; the alias has 23000 left, the first address 51000 and the second never expires; the smallest wins |
| `dns.get_answer_ttl(20000, "origin.net")` | returns `41000`; the alias was not used |
| `dns.resolve(33000, "www.site.com")` | returns `None`; the alias expired at exactly 33000 |
| `dns.add_record(34000, "www.site.com", "10.9.9.9")` | returns `True`; the name is free now that its alias has expired |
| `dns.add_record(35000, "origin.net", "10.0.0.1")` | returns `False`; that address is still alive |
| `dns.resolve(61000, "origin.net")` | returns `["10.0.0.2"]`; the first address expired |
| `dns.get_answer_ttl(61001, "origin.net")` | returns `-1`; only permanent records were used |
| `dns.add_record(62000, "origin.net", "10.0.0.1")` | returns `True`; an expired address can be added again, and goes to the end |
| `dns.resolve(63000, "origin.net")` | returns `["10.0.0.2", "10.0.0.1"]` |
| `dns.get_answer_ttl(64000, "nowhere.net")` | returns `None`; the name does not resolve |
