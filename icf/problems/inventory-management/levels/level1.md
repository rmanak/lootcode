Initially, the warehouse is empty, so implement operations to add items, copy
an item to a new name, and look up how many units of an item are in stock.

```python
add_item(self, name: str, quantity: int) -> bool
```

should add a new item `name` to the inventory with `quantity` units. Returns
`True` if the item was successfully added, or `False` if an item with the same
name already exists — in which case its quantity does not change.

```python
copy_item(self, name_from: str, name_to: str) -> bool
```

should copy the item `name_from` to a new item `name_to` with the same quantity.
The original item stays exactly as it is, and from then on the two items are
independent. Returns `True` if the item was successfully copied, or `False`
otherwise. Specifically:

- Returns `False` if `name_from` doesn't exist.
- Returns `False` if an item named `name_to` already exists — which includes
  copying an item onto itself.

```python
get_item_quantity(self, name: str) -> int | None
```

should return the quantity of the item `name`, or `None` if it doesn't exist.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `inv = InventoryManager()` | an empty warehouse |
| `inv.add_item("/warehouse/sectionA/item1", 20)` | returns `True`; inventory state: `{"/warehouse/sectionA/item1": 20}` |
| `inv.copy_item("/not-existing.item", "/warehouse/sectionB/item1")` | returns `False`; the item `"/not-existing.item"` doesn't exist |
| `inv.copy_item("/warehouse/sectionA/item1", "/warehouse/sectionB/item1")` | returns `True`; inventory state: `{"/warehouse/sectionA/item1": 20, "/warehouse/sectionB/item1": 20}` |
| `inv.add_item("/warehouse/sectionB/item1", 35)` | returns `False`; the item `"/warehouse/sectionB/item1"` already exists |
| `inv.copy_item("/warehouse/sectionB/item1", "/warehouse/sectionA/item1")` | returns `False`; the item `"/warehouse/sectionA/item1"` already exists |
| `inv.get_item_quantity("/warehouse/sectionB/item1")` | returns `20` |
| `inv.get_item_quantity("/not-existing.item")` | returns `None` |
