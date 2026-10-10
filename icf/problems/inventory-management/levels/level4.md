Space in the warehouse is tight, so items that are not needed right away can be
**packed**. Packing stores an item's stock in compact form: the item `<name>` is
replaced by an item named `<name>.packed` that holds half as many units — and so
takes up only half as much of its owner's capacity. Unpacking reverses this.
Implement operations to pack an item and to unpack it again.

```python
pack_item(self, user_id: str, name: str) -> int | None
```

should pack the item `name` owned by `user_id`: the item `name` is removed, and
a new item named `name + ".packed"` is added with **half** the original
quantity, owned by the same user. It is guaranteed that an item being packed has
an even quantity. Returns the user's remaining capacity after packing, or
`None` otherwise. Specifically:

- Returns `None` if `user_id` doesn't exist.
- Returns `None` if the item `name` doesn't exist, or is not owned by
  `user_id`.
- Returns `None` if `name` already ends with `".packed"` — a packed item cannot
  be packed again.
- Returns `None` if an item named `name + ".packed"` already exists.

```python
unpack_item(self, user_id: str, name: str) -> int | None
```

should unpack the item `name + ".packed"` owned by `user_id` — note that `name`
is the original name, **without** the suffix. The packed item is removed, and
the item `name` is added back with **twice** the packed quantity, owned by the
same user. Returns the user's remaining capacity after unpacking, or `None`
otherwise. Specifically:

- Returns `None` if `user_id` doesn't exist.
- Returns `None` if the item `name + ".packed"` doesn't exist, or is not owned
  by `user_id`.
- Returns `None` if an item named `name` already exists.
- Returns `None` if the unpacked item would make the user's total exceed their
  capacity.

### Additional conditions

- A packed item is an ordinary item in every other respect: `get_item_quantity`,
  `find_items` and `update_capacity` all see it with its packed quantity.
- `add_item` and `add_item_by` are never called with a name that ends with
  `".packed"`.
- `copy_item` preserves packing: `name_to` ends with `".packed"` exactly when
  `name_from` does. The copy of a packed item is therefore a packed item too,
  and can be unpacked under its own name.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `inv = InventoryManager()` | an empty warehouse with no users |
| `inv.add_user("ana", 1000)` | returns `True` |
| `inv.add_item_by("ana", "/bolts", 400)` | returns `600` |
| `inv.add_item_by("ana", "/nuts", 300)` | returns `300` |
| `inv.pack_item("ana", "/bolts")` | returns `500`; inventory state: `{"/nuts": 300, "/bolts.packed": 200}` |
| `inv.get_item_quantity("/bolts")` | returns `None`; the item was replaced by its packed form |
| `inv.add_item_by("ana", "/washers", 400)` | returns `100` |
| `inv.unpack_item("ana", "/bolts")` | returns `None`; unpacking would add 200 units, but only 100 are left |
| `inv.update_capacity("ana", 1200)` | returns `0` |
| `inv.unpack_item("ana", "/bolts")` | returns `100`; inventory state: `{"/nuts": 300, "/washers": 400, "/bolts": 400}` |
| `inv.pack_item("ana", "/bolts")` | returns `300` |
| `inv.copy_item("/bolts.packed", "/spare/bolts.packed")` | returns `True`; the copy is a packed item owned by `"ana"` |
| `inv.add_item_by("ana", "/bolts", 50)` | returns `50`; the name `"/bolts"` is free while that item is packed |
| `inv.unpack_item("ana", "/bolts")` | returns `None`; an item named `"/bolts"` exists |
| `inv.pack_item("ana", "/bolts.packed")` | returns `None`; the item is already packed |
| `inv.add_user("ben", 500)` | returns `True` |
| `inv.pack_item("ben", "/nuts")` | returns `None`; `"/nuts"` is owned by `"ana"` |
| `inv.pack_item("ana", "/nuts")` | returns `200` |
| `inv.unpack_item("ana", "/spare/bolts")` | returns `0`; inventory state: `{"/washers": 400, "/bolts.packed": 200, "/bolts": 50, "/nuts.packed": 150, "/spare/bolts": 400}` |
