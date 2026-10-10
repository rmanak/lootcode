The warehouse has grown, and staff need to find things in it. Implement an
operation to find all items whose names start with a given prefix and end with
a given suffix — for example, every item in one section of the warehouse, or
every item of one kind wherever it is kept.

```python
find_items(self, prefix: str, suffix: str) -> list[str]
```

should return all items whose name starts with `prefix` and ends with `suffix`,
as a list of strings in the following format:

```
["<name_1>(<quantity_1>)", "<name_2>(<quantity_2>)", ..., "<name_n>(<quantity_n>)"]
```

The items are sorted by quantity in descending order; items with the same
quantity are sorted by name in ascending lexicographic order. Returns an empty
list if no item matches.

Additional conditions:

- The prefix and the suffix are checked independently, and they may overlap:
  the name `"/ab"` starts with `"/a"` and ends with `"ab"`, so it matches both.
- An empty prefix or suffix matches every name on that side; with both empty,
  every item matches.
- Matching is case-sensitive and uses plain string operations, so the prefix
  `"/warehouse"` also matches `"/warehouse2/item"`.
- "Lexicographic" means ordinary string comparison: uppercase letters come
  before lowercase ones, and `"/a10"` comes before `"/a9"`.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `inv = InventoryManager()` | an empty warehouse |
| `inv.add_item("/warehouse/sectionX/itemA", 50)` | returns `True` |
| `inv.add_item("/warehouse/itemB", 25)` | returns `True` |
| `inv.add_item("/warehouse/sectionY/itemC", 30)` | returns `True` |
| `inv.copy_item("/warehouse/sectionY/itemC", "/warehouse/sectionZ/itemC")` | returns `True` |
| `inv.find_items("/warehouse/", "")` | returns `["/warehouse/sectionX/itemA(50)", "/warehouse/sectionY/itemC(30)", "/warehouse/sectionZ/itemC(30)", "/warehouse/itemB(25)"]`; the two items with 30 units are ordered by name |
| `inv.find_items("/warehouse/section", "itemC")` | returns `["/warehouse/sectionY/itemC(30)", "/warehouse/sectionZ/itemC(30)"]` |
| `inv.find_items("/warehouse", "itemX")` | returns `[]`; no name ends with `"itemX"` |
| `inv.find_items("/sectionY", "itemC")` | returns `[]`; names must *start* with the prefix |
| `inv.find_items("", "B")` | returns `["/warehouse/itemB(25)"]`; the empty prefix matches every name |
| `inv.find_items("/warehouse/itemB", "itemB")` | returns `["/warehouse/itemB(25)"]`; the prefix and the suffix may overlap |
