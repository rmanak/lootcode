### Instructions

Your task is to implement a simplified version of a parking lot management
system. A parking lot has several levels, and each level is a row of parking
spots. Drivers arrive, the system picks a spot for their vehicle, and later
they leave and pay. The system you are building is what the barrier at the
entrance talks to: it decides where every vehicle goes, knows where every
vehicle is, and keeps track of what each stay costs. Everything is kept in
memory, and every operation carries the timestamp at which it happens.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `ParkingLot`. Plan your design according to the level
specifications below:

- **Level 1:** The parking lot should support adding levels, parking and
  removing motorcycles and cars, and finding where a vehicle is parked.
- **Level 2:** The parking lot should support counting free spots and ranking
  levels by how much room they have left.
- **Level 3:** The parking lot should support buses, which take up several
  spots at once, and listing the vehicles on a level.
- **Level 4:** The parking lot should support hourly parking rates, the fee
  for each stay, and a record of past stays and of the money collected.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **level** has an identifier, such as `"G"` or `"P1"`, and a **layout**: a
string with one character per spot, from left to right.

- `'M'` is a motorcycle spot.
- `'R'` is a regular spot.

Each spot's identifier is the level's identifier, a dash, and the spot's
position on that level counting from `0`. The level `"G"` with layout `"MRR"`
has the spots `"G-0"` (motorcycle), `"G-1"` (regular) and `"G-2"` (regular).

A vehicle is identified by its licence **plate**, such as `"KX-512"`.

### Notes

- Timestamps are non-negative integers measured in milliseconds, and they
  strictly increase from one call to the next within a test.
- Levels are searched in the order they were added, and the spots on a level
  from left to right. Whenever the statement says "the first free spot", it
  means first in that order.
- Level identifiers are non-empty strings of letters and digits. Plates are
  non-empty strings of letters, digits and dashes. Layouts are non-empty and
  contain only `'M'` and `'R'`.
- A fresh `ParkingLot()` has no levels, so nothing can park until a level is
  added.
