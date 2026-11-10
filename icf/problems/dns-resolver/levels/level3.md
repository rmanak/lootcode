When a name cannot be resolved, an operator can configure **fallbacks**:
other names to try instead, in order. Not every failure deserves a fallback,
though. A missing record is a normal miss, and trying the next option is the
right response; an alias loop is a configuration error, and hiding it behind a
fallback would make it impossible to notice. So a missing record falls through
to the next fallback, while a loop is reported immediately.

```python
add_fallback(self, timestamp: int, name: str, fallback: str) -> bool
```

should append `fallback` to the list of fallbacks of `name`. Returns `True` if
it was added, or `False` if `fallback` is the same name as `name`, or is
already in the list of fallbacks of `name`. Fallbacks can be configured for
any name, whether or not it has records. They are never removed.

```python
get_status(self, timestamp: int, name: str) -> str
```

should resolve `name` (as described below) and report the outcome:

- `"RESOLVED"` if the resolution produced addresses;
- `"LOOP"` if it was stopped by an alias loop;
- `"NOT_FOUND"` otherwise.

### How a name is resolved

To resolve a name:

1. Follow its chain of aliases, as in level 2. If the chain is a loop, the
   resolution **stops** with the outcome `"LOOP"`.
2. If the name at the end of the chain has addresses, the outcome is
   `"RESOLVED"` with those addresses.
3. Otherwise, try the fallbacks of the name being resolved, in the order they
   were added. Each fallback is resolved in full by these same steps,
   including its own aliases and its own fallbacks:
   - if it ends in `"RESOLVED"`, that is the outcome — its addresses are the
     answer, and no further fallbacks are tried;
   - if it ends in `"LOOP"`, the whole resolution stops with `"LOOP"` — the
     error propagates, and no further fallbacks are tried;
   - if it ends in `"NOT_FOUND"`, move on to the next fallback.
4. If no fallback produced an answer, the outcome is `"NOT_FOUND"`.

Additional rules:

- Only the fallbacks of the name being resolved are used — not the fallbacks
  of the names its aliases pass through.
- Within one resolution, a name that has already been resolved (the name
  originally asked for, or a fallback that was already tried) is skipped if it
  appears again as a fallback. This is what keeps fallbacks that refer to each
  other from going on forever.

How the existing operations change:

- `resolve` returns the addresses when the outcome is `"RESOLVED"`, and `None`
  otherwise.
- `get_chain` is unchanged: it follows aliases only, never fallbacks.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `dns = Resolver()` | an empty zone |
| `dns.add_record(1, "eu.api.net", "10.1.0.1")` | returns `True` |
| `dns.add_alias(2, "us.api.net", "us-old.api.net")` | returns `True`; a dead end: us-old.api.net has no addresses |
| `dns.add_fallback(3, "api.net", "us.api.net")` | returns `True` |
| `dns.add_fallback(4, "api.net", "eu.api.net")` | returns `True` |
| `dns.add_fallback(5, "api.net", "US.api.net.")` | returns `False`; already a fallback of `"api.net"` |
| `dns.resolve(6, "api.net")` | returns `["10.1.0.1"]`; api.net has no addresses; us.api.net is NOT_FOUND, so eu.api.net is tried and answers |
| `dns.get_status(7, "api.net")` | returns `"RESOLVED"` |
| `dns.get_status(8, "us.api.net")` | returns `"NOT_FOUND"` |
| `dns.add_alias(9, "us-old.api.net", "us.api.net")` | returns `True`; now us.api.net → us-old.api.net → us.api.net is a loop |
| `dns.get_status(10, "api.net")` | returns `"LOOP"`; the first fallback hit a loop, so the whole resolution stops |
| `dns.resolve(11, "api.net")` | returns `None`; eu.api.net is never tried |
| `dns.get_chain(12, "api.net")` | returns `["api.net"]`; get_chain does not follow fallbacks |
