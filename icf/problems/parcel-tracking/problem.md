### Instructions

Your task is to implement a simplified version of a parcel tracking system. A
delivery company scans every parcel many times on its way — when it is picked
up, sorted, loaded, delayed, delivered — and each scan is an **event**. The
system keeps a tally of those events for every parcel, and later also tracks
which courier is carrying each parcel. Everything is kept in memory.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `ParcelTracker`. Plan your design according to the level
specifications below:

- **Level 1:** The parcel tracking system should support recording events for
  parcels, reading event tallies, and removing an event type.
- **Level 2:** The parcel tracking system should support ranking parcels by
  how many events they have.
- **Level 3:** The parcel tracking system should support assigning couriers to
  parcels, and events recorded by the courier carrying a parcel.
- **Level 4:** The parcel tracking system should support undoing courier
  changes, and signing a courier out.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **parcel** is identified by a string `parcel_id`. For each **event type** —
also a string, such as `"scanned"` or `"delayed"` — it keeps a tally: how many
events of that type have been recorded for it. For example:

```
"p1"  →  {"scanned": 5, "delayed": 1}
```

### Notes

- A parcel exists while it has at least one event type with a tally. There is
  no separate operation to create or delete a parcel.
- Parcel ids, event types and courier ids are non-empty, case-sensitive
  strings.
- Event counts passed to the operations are positive integers.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `ParcelTracker()` has no parcels.
