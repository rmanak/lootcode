"""Level 2 — search and order (visible cases)."""
from icf_testkit import case, expect


def ids(results):
    return [r["id"] for r in results]


@case("everything is listed, simplest recipe first")
def all_recipes_sorted(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r2", "Tomato Soup", ["tomato", "stock", "cream"])
    book.add_recipe("r1", "Tomato Salad", ["tomato", "oil"])
    book.add_recipe("r3", "Toast", ["bread"])
    expect(ids(book.get_all_recipes()), ["r3", "r1", "r2"])


@case("search matches part of the name, ignoring case")
def search_is_case_insensitive(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Tomato Salad", ["tomato", "oil"])
    book.add_recipe("r2", "Tomato Soup", ["tomato", "stock", "cream"])
    book.add_recipe("r3", "Toast", ["bread"])
    expect(ids(book.search_recipes("tomato")), ["r1", "r2"])
    expect(ids(book.search_recipes("TOAST")), ["r3"])


@case("a search that matches nothing returns an empty list")
def search_no_match(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Toast", ["bread"])
    expect(book.search_recipes("pizza"), [])


@case("an empty book lists and searches as empty")
def empty_book(RecipeManager):
    book = RecipeManager()
    expect(book.get_all_recipes(), [])
    expect(book.search_recipes("anything"), [])


@case("recipes with the same number of ingredients are ordered by id, as text")
def ties_order_by_id_as_text(RecipeManager):
    book = RecipeManager()
    for recipe_id, name in (("r9", "Nine"), ("r10", "Ten"), ("r1", "One")):
        book.add_recipe(recipe_id, name, ["x"])
    expect(ids(book.get_all_recipes()), ["r1", "r10", "r9"])


@case("a search result carries the whole recipe")
def results_are_full_recipes(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Toast", ["bread"])
    expect(book.search_recipes("toast"),
           [{"id": "r1", "name": "Toast", "ingredients": ["bread"]}])
