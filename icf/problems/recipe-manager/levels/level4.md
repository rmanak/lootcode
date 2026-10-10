Cooks keep changing each other's recipes, and sometimes a change turns out to be
a mistake. The recipe manager should keep the full version history of every
recipe, and allow rolling a recipe back to any earlier version.

From this level on, every successful change to a recipe **appends a new
version** instead of overwriting the old one:

- `add_recipe` creates a recipe at version `1`.
- Each successful `update_recipe`, `edit_recipe` or `rollback_recipe` appends
  the next version. A change that returns `False` adds no version.
- Version numbers start at `1`, go up by one with each change, and are never
  reused or reset.
- `get_recipe`, `search_recipes` and `get_all_recipes` keep returning the
  newest version of each recipe.
- Deleting a recipe deletes its history as well. If its id is used again later,
  the new recipe starts again at version `1`.

```python
get_recipe_history(self, recipe_id: str) -> list[dict] | None
```

should return every version of the recipe with identifier `recipe_id`, oldest
first, as a list in the following format:

```python
[{"version": 1, "name": ..., "ingredients": [...]}, {"version": 2, "name": ..., "ingredients": [...]}, ...]
```

Returns `None` if the recipe doesn't exist. Changing the returned list or its
entries must not change the stored history.

```python
rollback_recipe(self, user_id: str, recipe_id: str, version: int) -> bool
```

should restore the recipe with identifier `recipe_id` to the given version, on
behalf of the user `user_id`, by appending a **copy** of that version's name and
ingredients as the new newest version. The history is never shortened: rolling
a three-version recipe back to version 1 gives it a fourth version whose name
and ingredients match the first. Rolling back to the version the recipe is
already on still appends a new version.

Returns `True` if the rollback was successful, or `False` otherwise, in which
case nothing changes. Specifically:

- Returns `False` if `user_id` is not a registered user.
- Returns `False` if the recipe doesn't exist.
- Returns `False` if `version` is not one of the recipe's existing version
  numbers.
- Returns `False` if the name at that version is now used by a **different**
  recipe, compared case-insensitively. A recipe never conflicts with its own
  earlier names.

A successful rollback changes the recipe's current name, so the name it had
just before is freed for other recipes to use.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `book = RecipeManager()` | an empty recipe book with no users |
| `book.add_user("u1", "Ada")` | returns `True` |
| `book.add_recipe("r1", "Pasta", ["egg", "flour"])` | returns `True`; version 1 |
| `book.edit_recipe("u1", "r1", "Spaghetti", ["egg", "flour"])` | returns `True`; version 2 |
| `book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork"])` | returns `True`; version 3 |
| `book.rollback_recipe("u1", "r1", 1)` | returns `True`; appends version 4, a copy of version 1 |
| `book.get_recipe("r1")` | returns `{"id": "r1", "name": "Pasta", "ingredients": ["egg", "flour"]}` |
| `[v["version"] for v in book.get_recipe_history("r1")]` | returns `[1, 2, 3, 4]` |
| `[v["name"] for v in book.get_recipe_history("r1")]` | returns `["Pasta", "Spaghetti", "Carbonara", "Pasta"]`; the history was not truncated |
| `book.add_recipe("r2", "Carbonara", ["egg", "cheese"])` | returns `True`; `"r1"` is no longer called Carbonara, so the name is free |
| `book.rollback_recipe("u1", "r1", 3)` | returns `False`; the name at version 3 now belongs to recipe `"r2"` |
| `book.rollback_recipe("u1", "r1", 5)` | returns `False`; there is no version 5 |
| `book.rollback_recipe("u9", "r1", 2)` | returns `False`; `"u9"` is not a registered user |
| `len(book.get_recipe_history("r1"))` | returns `4`; rejected rollbacks add no version |
| `book.get_recipe_history("r9")` | returns `None`; there is no recipe `"r9"` |
