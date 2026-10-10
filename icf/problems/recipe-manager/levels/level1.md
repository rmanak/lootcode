Initially, the recipe book is empty, so implement operations to add a recipe,
read it back, update it, and delete it.

```python
add_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool
```

should add a new recipe with the given identifier, name and list of
ingredients. Returns `True` if the recipe was successfully added, or `False`
otherwise, in which case nothing changes. Specifically:

- Returns `False` if a recipe with `recipe_id` already exists.
- Returns `False` if `name` is already used by another recipe, compared
  case-insensitively.

```python
get_recipe(self, recipe_id: str) -> dict | None
```

should return the recipe with identifier `recipe_id`, in the form
`{"id": ..., "name": ..., "ingredients": [...]}`. Returns `None` if the recipe
doesn't exist.

```python
update_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool
```

should replace both the name and the ingredients of the recipe with identifier
`recipe_id`. Returns `True` if the recipe was successfully updated, or `False`
otherwise, in which case nothing changes. Specifically:

- Returns `False` if the recipe doesn't exist.
- Returns `False` if `name` is already used by a **different** recipe, compared
  case-insensitively. A recipe may keep its own name, or change only its
  capitalization — the uniqueness check never counts the recipe being updated.

```python
delete_recipe(self, recipe_id: str) -> bool
```

should remove the recipe with identifier `recipe_id`, freeing both its
identifier and its name for reuse. Returns `True` if the recipe was
successfully deleted, or `False` if it doesn't exist.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `book = RecipeManager()` | an empty recipe book |
| `book.add_recipe("r1", "Pasta", ["egg", "flour"])` | returns `True` |
| `book.add_recipe("r2", "PASTA", ["water"])` | returns `False`; `"PASTA"` is the same name as `"Pasta"` when case is ignored |
| `book.add_recipe("r1", "Risotto", ["rice"])` | returns `False`; the id `"r1"` is already taken |
| `book.add_recipe("r2", "Risotto", ["rice", "stock"])` | returns `True` |
| `book.get_recipe("r1")` | returns `{"id": "r1", "name": "Pasta", "ingredients": ["egg", "flour"]}` |
| `book.get_recipe("r9")` | returns `None`; there is no recipe `"r9"` |
| `book.update_recipe("r1", "Pasta", ["egg", "flour", "salt"])` | returns `True`; a recipe may keep its own name |
| `book.update_recipe("r1", "risotto", ["egg"])` | returns `False`; recipe `"r2"` already uses that name |
| `book.update_recipe("r9", "Soup", [])` | returns `False`; there is no recipe `"r9"` |
| `book.delete_recipe("r2")` | returns `True`; the id `"r2"` and the name `"Risotto"` are free again |
| `book.delete_recipe("r2")` | returns `False`; the recipe was already deleted |
| `book.update_recipe("r1", "risotto", ["egg", "rice"])` | returns `True`; the name is free now |
| `book.get_recipe("r1")` | returns `{"id": "r1", "name": "risotto", "ingredients": ["egg", "rice"]}`; the name is stored exactly as given |
