"""Level 3 — cooks (hidden cases)."""
from icf_testkit import case, expect


@case("update_recipe still works with no cook attached")
def update_still_works(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.update_recipe("r1", "Spaghetti", ["egg", "salt"]), True)
    expect(book.get_recipe("r1")["name"], "Spaghetti")


@case("a refused registration does not unregister the cook who holds the id")
def refused_registration_is_inert(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_user("u1", "Grace")
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.edit_recipe("u1", "r1", "Spaghetti", ["egg"]), True,
           "u1 is still a registered cook")


@case("two cooks can edit the same recipe in turn")
def two_cooks(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_user("u2", "Grace")
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.edit_recipe("u1", "r1", "Spaghetti", ["egg"]), True)
    expect(book.edit_recipe("u2", "r1", "Carbonara", ["egg", "pork"]), True)
    expect(book.get_recipe("r1")["name"], "Carbonara")


@case("editing a deleted recipe is refused, and its name is free to take")
def edit_after_delete(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.add_recipe("r2", "Risotto", ["rice"])
    book.delete_recipe("r1")
    expect(book.edit_recipe("u1", "r1", "Anything", []), False)
    expect(book.edit_recipe("u1", "r2", "pasta", ["rice"]), True,
           "the name was freed by the delete")


@case("an edit reaches the search results too")
def edit_is_visible_to_search(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.edit_recipe("u1", "r1", "Carbonara", ["egg", "pork"])
    expect(book.search_recipes("pasta"), [])
    expect([r["id"] for r in book.search_recipes("carb")], ["r1"])
