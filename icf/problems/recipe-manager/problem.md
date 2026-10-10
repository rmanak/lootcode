### Instructions

Your task is to implement a simplified version of a recipe manager — the back
end of a shared recipe book used by the kitchens of a small restaurant group.
Cooks add their recipes to the book, look them up by name, keep them up to
date, and, when a change turns out to be a mistake, go back to an earlier
version. All operations that should be supported by the recipe manager are
described in the levels below.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `RecipeManager`. Plan your design according to the level
specifications below:

- **Level 1:** The recipe manager should support adding, reading, updating and
  deleting recipes.
- **Level 2:** The recipe manager should support searching recipes by name and
  listing all recipes in a well-defined order.
- **Level 3:** The recipe manager should support registering users (cooks) and
  editing recipes on behalf of a registered user.
- **Level 4:** The recipe manager should keep a version history of every recipe
  and support rolling a recipe back to an earlier version.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **recipe** has an identifier that never changes, a display name, and a list
of ingredients. People find recipes by name, so **two recipes may never share a
name**, and names are compared case-insensitively: `"Pasta"`, `"pasta"` and
`"PASTA"` are the same name. A name is still stored and returned exactly as it
was given — only the comparison ignores case.

Whenever a recipe is returned, it is a dictionary of the form:

```python
{"id": "r1", "name": "Pasta", "ingredients": ["egg", "flour"]}
```

### Notes

- There are no timestamps in this task: operations happen in the order they
  are called.
- Recipe ids, names, ingredients, user ids and usernames are non-empty strings.
- An ingredient list may be empty and may repeat an ingredient; it is stored
  and returned in the order it was given.
- Lists are never shared between the caller and your storage: if a caller later
  changes a list they passed in, or a list you returned to them, the stored
  recipe must not change.
- A fresh `RecipeManager()` has no recipes and no users.
