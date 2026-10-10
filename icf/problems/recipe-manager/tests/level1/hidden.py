"""Level 1 — recipes (hidden cases)."""
from icf_testkit import case, expect


@case("the name is stored exactly as written, only the comparison ignores case")
def name_is_stored_verbatim(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "PaStA alla Norma", ["aubergine"])
    expect(book.get_recipe("r1")["name"], "PaStA alla Norma")
    expect(book.add_recipe("r2", "pasta ALLA norma", ["tomato"]), False)


@case("the caller's ingredient list is copied, not adopted")
def input_list_is_copied(RecipeManager):
    book = RecipeManager()
    ingredients = ["egg", "flour"]
    book.add_recipe("r1", "Pasta", ingredients)
    ingredients.append("sabotage")
    expect(book.get_recipe("r1")["ingredients"], ["egg", "flour"])

    replacement = ["rice"]
    book.update_recipe("r1", "Risotto", replacement)
    replacement.append("sabotage")
    expect(book.get_recipe("r1")["ingredients"], ["rice"])


@case("the returned ingredient list is a copy too")
def output_list_is_copied(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg"])
    got = book.get_recipe("r1")
    got["ingredients"].append("sabotage")
    got["name"] = "Something else"
    expect(book.get_recipe("r1")["ingredients"], ["egg"])
    expect(book.get_recipe("r1")["name"], "Pasta")


@case("ingredients keep their order and their repeats, and may be empty")
def ingredients_are_verbatim(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Butter Toast", ["butter", "bread", "butter"])
    book.add_recipe("r2", "Water", [])
    expect(book.get_recipe("r1")["ingredients"], ["butter", "bread", "butter"])
    expect(book.get_recipe("r2")["ingredients"], [])


@case("a refused add leaves the recipe that blocked it untouched")
def refused_add_is_inert(RecipeManager):
    book = RecipeManager()
    book.add_recipe("r1", "Pasta", ["egg", "flour"])
    book.add_recipe("r2", "pasta", ["nothing"])
    expect(book.get_recipe("r1")["ingredients"], ["egg", "flour"])
    expect(book.get_recipe("r2"), None)


@case("many recipes coexist without interfering")
def many_recipes(RecipeManager):
    book = RecipeManager()
    for index in range(30):
        expect(book.add_recipe(f"r{index}", f"Dish {index}", [f"i{index}"]), True)
    expect(book.get_recipe("r17"),
           {"id": "r17", "name": "Dish 17", "ingredients": ["i17"]})
    expect(book.delete_recipe("r17"), True)
    expect(book.get_recipe("r16")["name"], "Dish 16")
    expect(book.get_recipe("r17"), None)
