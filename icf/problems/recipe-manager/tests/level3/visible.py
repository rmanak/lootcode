"""Level 3 — cooks (visible cases)."""
from icf_testkit import case, expect


@case("a cook is registered once")
def add_user(RecipeManager):
    book = RecipeManager()
    expect(book.add_user("u1", "Ada"), True)
    expect(book.add_user("u1", "Grace"), False, "that id is taken")
    expect(book.add_user("u2", "Grace"), True, "a different id is fine")


@case("a registered cook can edit a recipe")
def edit_works(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg", "flour"])
    expect(book.edit_recipe("u1", "r1", "Spaghetti", ["egg", "flour", "salt"]), True)
    expect(book.get_recipe("r1"),
           {"id": "r1", "name": "Spaghetti",
            "ingredients": ["egg", "flour", "salt"]})


@case("an unregistered cook cannot edit anything")
def unknown_user_refused(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    expect(book.edit_recipe("u9", "r1", "Linguine", ["egg", "salt"]), False)
    expect(book.get_recipe("r1")["name"], "Pasta", "nothing changed")


@case("editing a recipe that is not there is refused")
def unknown_recipe_refused(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    expect(book.edit_recipe("u1", "r9", "Linguine", ["egg"]), False)


@case("the name rules apply to an edit exactly as they do to an update")
def edit_name_rules(RecipeManager):
    book = RecipeManager()
    book.add_user("u1", "Ada")
    book.add_recipe("r1", "Pasta", ["egg"])
    book.add_recipe("r2", "Risotto", ["rice"])
    expect(book.edit_recipe("u1", "r1", "PASTA", ["egg", "salt"]), True,
           "its own name, in different case")
    expect(book.edit_recipe("u1", "r1", "risotto", ["egg"]), False, "r2 has it")
    expect(book.get_recipe("r1")["name"], "PASTA")
