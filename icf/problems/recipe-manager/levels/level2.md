The app needs a list view and a search box, so implement operations to search
recipes by name and to list every recipe in the book, both in a well-defined
order.

```python
search_recipes(self, query: str) -> list[dict]
```

should return all recipes whose name contains `query` anywhere in it, compared
case-insensitively. Each recipe is returned in the same form as `get_recipe`
returns it. An empty `query` matches every recipe. Returns an empty list if no
recipe matches.

```python
get_all_recipes(self) -> list[dict]
```

should return all recipes in the book, in the same form as `get_recipe`
returns them. Returns an empty list if the book is empty.

### Ordering

Both operations return their recipes sorted by:

1. **the number of ingredients, ascending** — the simplest recipes come first;
2. **the recipe id, ascending**, to break ties between recipes with the same
   number of ingredients.

Recipe ids are compared as ordinary strings, so `"r10"` comes before `"r9"`,
and uppercase letters come before lowercase ones.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `book = RecipeManager()` | an empty recipe book |
| `book.add_recipe("r2", "Tomato Soup", ["tomato", "stock", "cream"])` | returns `True`; 3 ingredients |
| `book.add_recipe("r1", "Tomato Salad", ["tomato", "oil"])` | returns `True`; 2 ingredients |
| `book.add_recipe("r3", "Toast", ["bread"])` | returns `True`; 1 ingredient |
| `book.add_recipe("r10", "Green Salad", ["lettuce", "oil"])` | returns `True`; 2 ingredients |
| `[r["id"] for r in book.get_all_recipes()]` | returns `["r3", "r1", "r10", "r2"]`; `"r1"` and `"r10"` both have 2 ingredients, so they are ordered by id |
| `[r["id"] for r in book.search_recipes("tomato")]` | returns `["r1", "r2"]` |
| `[r["id"] for r in book.search_recipes("SALAD")]` | returns `["r1", "r10"]`; case is ignored |
| `book.search_recipes("oas")` | returns `[{"id": "r3", "name": "Toast", "ingredients": ["bread"]}]`; the query may match anywhere in the name |
| `book.search_recipes("pizza")` | returns `[]` |
