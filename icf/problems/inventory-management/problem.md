### Instructions

Your task is to implement a simplified version of an inventory management
system for a shared warehouse. Every item in the warehouse is recorded under a
unique name that says where it is kept — such as
`"/warehouse/sectionA/bolts"` — together with the number of units in stock.
Staff add items, copy an item's stock to a new location, and look items up.
As the system grows, several users share the warehouse, each with a limited
amount of stock they may own, and items can be packed to save space. All
operations that should be supported by the system are described in the levels
below.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `InventoryManager`. Plan your design according to the
level specifications below:

- **Level 1:** The inventory management system should support adding items,
  copying items, and getting the quantity of an item.
- **Level 2:** The inventory management system should support finding items
  whose names start with a given prefix and end with a given suffix.
- **Level 3:** The inventory management system should support users who own
  items, each with a limited stock capacity.
- **Level 4:** The inventory management system should support packing an item
  so that it takes up half the space, and unpacking it again.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so plan a data model you can extend rather than one you will have to replace.

### The data model

An **item** has a name and a quantity: the number of units in stock. Item names
are unique across the whole warehouse and case-sensitive. They look like paths,
but they are plain strings — neither `/` nor `.` has any special meaning, so
`"/a/b"` and `"/a/b/"` are simply two different names.

### Notes

- There are no timestamps in this task: operations happen in the order they
  are called.
- Item names and user ids are non-empty strings. Quantities are positive
  integers, and capacities are non-negative integers.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `InventoryManager()` has no items and no users.
