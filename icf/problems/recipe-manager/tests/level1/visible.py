"""Level 1 — recipes (visible cases)."""
from icf_testkit import case, expect


@case("a recipe can be added and read back")
def add_and_get(RecipeManager):
    book = RecipeManager()
    expect(book.add_recipe("r1", "Pasta", ["egg", "flour"]), True)
    expect(book.get_recipe("r1"),
           {"id": "r1", "name": "Pasta", "ingredients": ["egg", "flour"]})


@case("an id or a name can only be used once, and names ignore case")
def duplicates_are_refused(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.add_recipe("r1", "Risotto", ["rice"]), False, "that id is taken")
    expect(book.add_recipe("r2", "PASTA", ["water"]), False, "that name is taken")
    expect(book.add_recipe("r2", "Risotto", ["rice"]), True)


@case("an unknown recipe reads as None")
def get_missing(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.get_recipe("r1")["name"], "Pasta")
    expect(book.get_recipe("r9"), None)


@case("update replaces the name and the ingredients")
def update_replaces(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg", "flour"])
    expect(book.update_recipe("r1", "Spaghetti", ["egg", "flour", "salt"]), True)
    expect(book.get_recipe("r1"),
           {"id": "r1", "name": "Spaghetti",
            "ingredients": ["egg", "flour", "salt"]})


@case("a recipe may keep its own name but not take another's")
def update_name_rules(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    book.add_recipe("r2", "Risotto", ["rice"])
    expect(book.update_recipe("r1", "Pasta", ["egg", "salt"]), True,
           "its own name is not a clash")
    expect(book.update_recipe("r1", "risotto", ["egg"]), False, "r2 has that name")
    expect(book.get_recipe("r1")["ingredients"], ["egg", "salt"],
           "the refused update changed nothing")
    expect(book.update_recipe("r9", "Anything", []), False, "no such recipe")


@case("deleting frees both the id and the name")
def delete_frees(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.delete_recipe("r1"), True)
    expect(book.delete_recipe("r1"), False, "already gone")
    expect(book.get_recipe("r1"), None)
    expect(book.add_recipe("r1", "pasta", ["water"]), True,
           "the id and the name are both free again")
