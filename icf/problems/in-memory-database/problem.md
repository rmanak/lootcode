### Instructions

Your task is to implement a simplified version of an in-memory database. A
database like this stores the small pieces of data an application needs to
read and write quickly — user profiles, configuration settings, session tokens
— and keeps all of it in memory rather than on disk. All operations that should
be supported by this database are described in the levels below.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `Database`. Plan your design according to the level
specifications below:

- **Level 1:** The in-memory database should support basic operations to
  manipulate records, fields, and values within fields.
- **Level 2:** The in-memory database should support displaying a specific
  record's fields based on a filter.
- **Level 3:** The in-memory database should support TTL (Time-To-Live)
  settings on fields, so that values can expire.
- **Level 4:** The in-memory database should support backup and restore
  functionality.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so plan a data model you can extend rather than one you will have to replace.

### The data model

The database contains **records**. Each record is accessed with a unique
identifier `key` of string type, and holds any number of **field-value pairs**,
where both the field and the value are strings. For example, a record for a
user might look like this:

```
"user:42"  →  {"name": "Ada", "role": "admin", "session": "b17f"}
```

### Notes

- Every operation takes a `timestamp`: a non-negative integer, measured in
  milliseconds, that strictly increases from one call to the next within a
  test. Levels 1 and 2 do not need it, but level 3 does. The only exception to
  "strictly increasing" is the `at_timestamp` argument introduced in level 4,
  which names a moment in the past.
- Keys and field names are non-empty strings. Values are strings and may be
  empty — an empty string is still a value.
- A field name is unique within its record; different records may use the same
  field names.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `Database()` is empty.
