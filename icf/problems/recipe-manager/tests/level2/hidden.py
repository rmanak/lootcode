"""Level 2 — search and order (hidden cases)."""
from icf_testkit import case, expect


def ids(results):
    return [r["id"] for r in results]


@case("the query may match anywhere in the name")
def query_matches_anywhere(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Slow-roast Tomato Ragu", ["tomato"])
    expect(ids(book.search_recipes("roast tomato")), ["r1"])
    expect(ids(book.search_recipes("ragu")), ["r1"])
    expect(ids(book.search_recipes("agu")), ["r1"])


@case("an empty query matches every recipe")
def empty_query(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "One", ["a"])
    book.add_recipe("r2", "Two", ["a", "b"])
    expect(ids(book.search_recipes("")), ["r1", "r2"])


@case("a deleted recipe is in neither list")
def deleted_disappears(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Toast", ["bread"])
    book.add_recipe("r2", "Tomato Soup", ["tomato", "stock"])
    book.delete_recipe("r1")
    expect(ids(book.get_all_recipes()), ["r2"])
    expect(book.search_recipes("toast"), [])


@case("an update is reflected in both the search and the order")
def update_changes_results(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Toast", ["bread"])
    book.add_recipe("r2", "Soup", ["stock"])
    expect(ids(book.get_all_recipes()), ["r1", "r2"])
    book.update_recipe("r1", "Fancy Toast", ["bread", "butter", "truffle"])
    expect(ids(book.get_all_recipes()), ["r2", "r1"], "r1 now has more work")
    expect(ids(book.search_recipes("fancy")), ["r1"])
    expect(book.search_recipes("Toast")[0]["name"], "Fancy Toast")


@case("mutating a result does not reach back into the book")
def results_are_detached(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Toast", ["bread"])
    results = book.get_all_recipes()
    results[0]["ingredients"].append("sabotage")
    results.clear()
    expect(book.get_all_recipes()[0]["ingredients"], ["bread"])


@case("capitals sort before lower case when ids tie on ingredient count")
def id_ordering_is_ascii(RecipeManager):
    book = RecipeManager()
    for recipe_id in ("beta", "Alpha", "alpha2"):
        book.add_recipe(recipe_id, f"Dish {recipe_id}", ["x"])
    expect(ids(book.get_all_recipes()), ["Alpha", "alpha2", "beta"])
