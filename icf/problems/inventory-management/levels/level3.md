Implement support for different users managing stock in the warehouse. All
users share one common inventory, but each user owns the items they add and is
given an individual **stock capacity**: the most units they may own in total.

```python
add_user(self, user_id: str, capacity: int) -> bool
```

should add a new user with `capacity` as their stock limit, in units. The total
quantity of all items owned by `user_id` may never exceed `capacity`. Returns
`True` if the user was successfully created, or `False` if a user with
`user_id` already exists — in which case that user's capacity does not change.

```python
add_item_by(self, user_id: str, name: str, quantity: int) -> int | None
```

should add a new item in the same way as `add_item`, but the item is owned by
`user_id`. Returns the user's **remaining capacity** after the item was added —
their capacity minus the total quantity of all the items they own — or `None`
otherwise. Specifically:

- Returns `None` if `user_id` doesn't exist.
- Returns `None` if an item named `name` already exists.
- Returns `None` if adding the item would make the user's total exceed their
  capacity. Filling the capacity exactly is allowed, and leaves `0`.

```python
update_capacity(self, user_id: str, capacity: int) -> int | None
```

should change the stock capacity of `user_id` to `capacity`. If the total
quantity of the user's items now exceeds the new capacity, the user's items are
removed from the inventory one at a time — **the largest quantity first**, and
among items with the same quantity, the one whose name comes first
lexicographically — until the total of the remaining items no longer exceeds
`capacity`. Removed items are gone for good, and their names are free to use
again. Returns the number of items removed (`0` if everything fits), or `None`
if `user_id` doesn't exist.

### How the existing operations change

- Items added with `add_item` from level 1 are owned by the special user
  `"admin"`, who has **unlimited** capacity. `"admin"` is never passed as the
  `user_id` of any other operation.
- `copy_item` preserves ownership: the copy is owned by the owner of the
  original item. If that owner is a user with a capacity, the copy counts
  against it, and `copy_item` returns `False` if the copy would not fit.
- `get_item_quantity` and `find_items` see every item, whoever owns it.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `inv = InventoryManager()` | an empty warehouse with no users |
| `inv.add_user("user1", 1500)` | returns `True`; creates `"user1"` with a capacity of 1500 |
| `inv.add_user("user1", 1200)` | returns `False`; `"user1"` already exists |
| `inv.add_user("user2", 2500)` | returns `True` |
| `inv.add_item_by("user1", "/sectionA/itemBig", 600)` | returns `900` |
| `inv.add_item_by("user1", "/itemMed", 400)` | returns `500` |
| `inv.copy_item("/itemMed", "/sectionA/itemMed")` | returns `True`; the copy is owned by `"user1"`, who now has 100 units left |
| `inv.add_item_by("user1", "/itemSmall", 200)` | returns `None`; `"user1"` does not have enough capacity left |
| `inv.add_item_by("user1", "/sectionA/itemTiny", 100)` | returns `0`; the item fills the capacity exactly |
| `inv.add_item_by("user2", "/itemMed", 500)` | returns `None`; the item `"/itemMed"` already exists |
| `inv.add_item("/storage/crate", 5000)` | returns `True`; owned by `"admin"`, who has unlimited capacity |
| `inv.add_item_by("user2", "/storage/itemHuge", 2500)` | returns `0` |
| `inv.add_item_by("user3", "/storage/itemHuge2", 10)` | returns `None`; `"user3"` doesn't exist |
| `inv.update_capacity("user1", 4000)` | returns `0`; all of `"user1"`'s items fit |
| `inv.update_capacity("user1", 700)` | returns `2`; `"user1"` owns 1500 units, so `"/sectionA/itemBig"` (600) is removed first, then `"/itemMed"` (400, whose name comes before `"/sectionA/itemMed"`), leaving 500 |
| `inv.get_item_quantity("/itemMed")` | returns `None`; the item was removed |
| `inv.get_item_quantity("/sectionA/itemMed")` | returns `400` |
| `inv.update_capacity("user3", 100)` | returns `None`; `"user3"` doesn't exist |
| `inv.add_item_by("user1", "/itemMed", 200)` | returns `0`; the removed item's name is free again |
