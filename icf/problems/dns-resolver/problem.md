### Instructions

Your task is to implement a simplified version of a DNS resolver. The Domain
Name System turns a name people can remember, like `example.com`, into the IP
addresses computers connect to. The resolver you are building holds a small
**zone** of records in memory — which names have which addresses, which names
are aliases for other names — and answers lookups against it.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `Resolver`. Plan your design according to the level
specifications below:

- **Level 1:** The resolver should support adding and removing address
  records, and resolving a name to its addresses.
- **Level 2:** The resolver should support aliases — names that point at other
  names — including chains of aliases and detecting loops.
- **Level 3:** The resolver should support fallback names to try when a name
  cannot be resolved, and report why a resolution failed.
- **Level 4:** The resolver should support records that expire, and report how
  long an answer remains valid.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so plan a data model you can extend rather than one you will have to replace.

### Names

Every name passed to any operation is **normalized** before it is used:

- Names are case-insensitive: `"Example.COM"` and `"example.com"` are the same
  name. The normalized form is all lowercase.
- A single trailing dot is ignored: `"example.com."` is the same name as
  `"example.com"`.

So `"Example.COM."` normalizes to `"example.com"`. Whenever an operation returns
a name, it returns the normalized form. Addresses (`ip`) are **not**
normalized: they are compared exactly as given.

### Notes

- Every operation takes a `timestamp`: a non-negative integer, measured in
  milliseconds, that strictly increases from one call to the next within a
  test. Levels 1 to 3 do not need it, but level 4 does.
- Names and addresses are non-empty strings, and a name never ends in more than
  one dot.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `Resolver()` has no records.
