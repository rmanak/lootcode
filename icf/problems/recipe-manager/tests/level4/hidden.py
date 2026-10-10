"""Level 4 — history and rollback (hidden cases)."""
from icf_testkit import case, expect


def names(history):
    return [entry["name"] for entry in history]


def versions(history):
    return [entry["version"] for entry in history]


@case("version numbers keep counting up through repeated rollbacks")
def versions_are_never_reused(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "One", ["a"])
    book.edit_recipe("u1", "r1", "Two", ["a", "b"])
    book.rollback_recipe("u1", "r1", 1)      # v3 = One
    book.rollback_recipe("u1", "r1", 2)      # v4 = Two
    book.rollback_recipe("u1", "r1", 3)      # v5 = One
    history = book.get_recipe_history("r1")
    expect(versions(history), [1, 2, 3, 4, 5])
    expect(names(history), ["One", "Two", "One", "Two", "One"])


@case("rolling back to the version you are already on still adds one")
def rollback_to_current(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.rollback_recipe("u1", "r1", 1), True,
           "a recipe never conflicts with its own earlier name")
    expect(versions(book.get_recipe_history("r1")), [1, 2])
    expect(book.get_recipe("r1")["name"], "Pasta")


@case("a rollback frees the name it moved away from")
def rollback_releases_the_old_name(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork"])
    book.rollback_recipe("u1", "r1", 1)                 # back to "Pasta"
    expect(book.add_recipe("r2", "CARBONARA", ["pork"]), True,
           "nothing is called Carbonara any more")
    expect(book.add_recipe("r3", "pasta", ["egg"]), False, "r1 is Pasta again")


@case("history entries are copies — editing one does not rewrite the past")
def history_entries_are_copies(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    history = book.get_recipe_history("r1")
    history[0]["ingredients"].append("sabotage")
    history[0]["name"] = "Hacked"
    expect(book.get_recipe_history("r1"),
           [{"version": 1, "name": "Pasta", "ingredients": ["egg"]}])
    expect(book.get_recipe("r1")["name"], "Pasta")


@case("a refused edit adds no version")
def refused_changes_add_no_version(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.add_recipe("r2", "Risotto", ["rice"])
    book.edit_recipe("u9", "r1", "Linguine", ["egg"])        # unknown cook
    book.edit_recipe("u1", "r1", "RISOTTO", ["egg"])         # name clash
    book.update_recipe("r1", "risotto", ["egg"])             # same clash
    expect(versions(book.get_recipe_history("r1")), [1])


@case("deleting a recipe takes its history with it")
def delete_clears_history(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.edit_recipe("u1", "r1", "Spaghetti", ["egg"])
    book.delete_recipe("r1")
    expect(book.get_recipe_history("r1"), None)
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(versions(book.get_recipe_history("r1")), [1], "a fresh history")


@case("the ingredients of an old version are exactly what they were")
def old_ingredients_are_preserved(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    original = ["egg", "flour"]
    book.add_recipe("r1", "Pasta", original)
    original.append("sabotage")
    book.edit_recipe("u1", "r1", "Spaghetti", ["egg", "flour", "salt"])
    book.rollback_recipe("u1", "r1", 1)
    expect(book.get_recipe("r1")["ingredients"], ["egg", "flour"])
    expect(book.get_recipe_history("r1")[0]["ingredients"], ["egg", "flour"])


@case("history and search stay in step after a rollback")
def rollback_updates_search(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork", "cheese"])
    expect([r["id"] for r in book.search_recipes("carbonara")], ["r1"])
    book.rollback_recipe("u1", "r1", 1)
    expect(book.search_recipes("carbonara"), [])
    expect([r["id"] for r in book.search_recipes("pasta")], ["r1"])
    expect(book.get_all_recipes()[0]["ingredients"], ["egg"],
           "the ingredient count went back down too")
