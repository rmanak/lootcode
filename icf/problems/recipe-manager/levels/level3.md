Recipes are now edited by the cooks who use the book, and the kitchen wants
every change to come from someone it knows. Implement operations to register
users and to edit a recipe on behalf of a registered user.

```python
add_user(self, user_id: str, username: str) -> bool
```

should register a new user with the given identifier and username. Returns
`True` if the user was successfully registered, or `False` if a user with
`user_id` already exists — in which case the existing user keeps their
username.

```python
edit_recipe(self, user_id: str, recipe_id: str, name: str, ingredients: list[str]) -> bool
```

should replace both the name and the ingredients of the recipe with identifier
`recipe_id`, on behalf of the user `user_id`. It works exactly like
`update_recipe`, with one extra condition: the user must be registered. Returns
`True` if the recipe was successfully edited, or `False` otherwise, in which
case nothing changes. Specifically:

- Returns `False` if `user_id` is not a registered user.
- Returns `False` if the recipe doesn't exist.
- Returns `False` if `name` is already used by a **different** recipe, compared
  case-insensitively. A recipe may keep its own name.

Any registered user may edit any recipe, and several users can edit the same
recipe one after another. `update_recipe` keeps working exactly as before,
without a user.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `book = RecipeManager()` | an empty recipe book with no users |
| `book.add_recipe("r1", "Pasta", ["egg", "flour"])` | returns `True` |
| `book.add_recipe("r2", "Risotto", ["rice"])` | returns `True` |
| `book.add_user("u1", "Ada")` | returns `True` |
| `book.add_user("u1", "Grace")` | returns `False`; the id `"u1"` is already registered |
| `book.add_user("u2", "Grace")` | returns `True` |
| `book.edit_recipe("u1", "r1", "Spaghetti", ["egg", "flour", "salt"])` | returns `True` |
| `book.edit_recipe("u9", "r1", "Linguine", ["egg"])` | returns `False`; `"u9"` is not a registered user |
| `book.edit_recipe("u1", "r9", "Linguine", ["egg"])` | returns `False`; there is no recipe `"r9"` |
| `book.edit_recipe("u2", "r1", "RISOTTO", ["egg"])` | returns `False`; recipe `"r2"` already uses that name |
| `book.edit_recipe("u2", "r1", "spaghetti", ["egg", "flour"])` | returns `True`; a different user may edit the same recipe, and it may keep its own name |
| `book.get_recipe("r1")` | returns `{"id": "r1", "name": "spaghetti", "ingredients": ["egg", "flour"]}` |
| `book.update_recipe("r2", "Risotto", ["rice", "stock"])` | returns `True`; `update_recipe` still works without a user |
