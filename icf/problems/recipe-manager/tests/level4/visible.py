"""Level 4 — history and rollback (visible cases)."""
from icf_testkit import case, expect


def names(history):
    return [entry["name"] for entry in history]


def versions(history):
    return [entry["version"] for entry in history]


@case("a new recipe has one version")
def history_starts_at_one(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.get_recipe_history("r1"),
           [{"version": 1, "name": "Pasta", "ingredients": ["egg"]}])


@case("every change appends a version")
def changes_append(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg", "flour"])
    book.update_recipe("r1", "Spaghetti", ["egg", "flour"])
    book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork"])
    history = book.get_recipe_history("r1")
    expect(versions(history), [1, 2, 3])
    expect(names(history), ["Pasta", "Spaghetti", "Carbonara"])
    expect(history[2]["ingredients"], ["egg", "pork"])


@case("rolling back appends a copy instead of truncating")
def rollback_appends(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg", "flour"])
    book.edit_recipe("u1", "r1", "Spaghetti", ["egg", "flour"])
    book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork"])
    expect(book.rollback_recipe("u1", "r1", 1), True)
    history = book.get_recipe_history("r1")
    expect(versions(history), [1, 2, 3, 4], "the history got longer, not shorter")
    expect(names(history), ["Pasta", "Spaghetti", "Carbonara", "Pasta"])


@case("the recipe itself reads as the version rolled back to")
def rollback_changes_the_current_recipe(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg", "flour"])
    book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork"])
    book.rollback_recipe("u1", "r1", 1)
    expect(book.get_recipe("r1"),
           {"id": "r1", "name": "Pasta", "ingredients": ["egg", "flour"]})


@case("a rollback is refused for an unknown cook, recipe or version")
def rollback_refusals(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.edit_recipe("u1", "r1", "Spaghetti", ["egg"])
    expect(book.rollback_recipe("u9", "r1", 1), False, "unknown cook")
    expect(book.rollback_recipe("u1", "r9", 1), False, "unknown recipe")
    expect(book.rollback_recipe("u1", "r1", 0), False, "versions start at 1")
    expect(book.rollback_recipe("u1", "r1", 3), False, "there is no version 3")
    expect(versions(book.get_recipe_history("r1")), [1, 2],
           "no refusal added a version")


@case("a rollback that would duplicate another recipe's name is refused")
def rollback_name_conflict(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork"])
    book.add_recipe("r2", "pasta", ["water"])       # the freed name, taken
    expect(book.rollback_recipe("u1", "r1", 1), False)
    expect(book.get_recipe("r1")["name"], "Carbonara", "nothing changed")


@case("the history of a recipe that does not exist is None")
def history_of_missing(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(len(book.get_recipe_history("r1")), 1)
    expect(book.get_recipe_history("r9"), None)
