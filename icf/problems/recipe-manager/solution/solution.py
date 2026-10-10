"""Reference solution — all four levels.

The shape that makes level 4 cheap is chosen at level 1: a recipe *is* a list
of versions, and "the recipe" is simply its last one. Adding history then
costs nothing, and `update`, `edit` and `rollback` all end in the same
`versions.append(...)`.

The other piece is a `name.lower() -> recipe_id` index, so the uniqueness rule
— which every single mutating method has to apply — is one dictionary lookup
rather than a scan.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Version:
    """One revision of a recipe."""

    name: str
    ingredients: list[str]

    def __post_init__(self) -> None:
        self.ingredients = list(self.ingredients)   # never alias the caller's list

    def as_view(self, recipe_id: str) -> dict:
        """The public shape of a recipe at this version."""
        return {"id": recipe_id, "name": self.name,
                "ingredients": list(self.ingredients)}


class RecipeManager:
    def __init__(self) -> None:
        self._recipes: dict[str, list[Version]] = {}   # newest version last
        self._by_name: dict[str, str] = {}             # name.lower() -> recipe_id
        self._users: dict[str, str] = {}

    # --- helpers -----------------------------------------------------------

    def _view(self, recipe_id: str) -> dict:
        return self._recipes[recipe_id][-1].as_view(recipe_id)

    def _name_taken_by_other(self, name: str, recipe_id: str) -> bool:
        owner = self._by_name.get(name.lower())
        return owner is not None and owner != recipe_id

    def _append_version(self, recipe_id: str, name: str,
                        ingredients: list[str]) -> None:
        versions = self._recipes[recipe_id]
        del self._by_name[versions[-1].name.lower()]
        versions.append(Version(name, ingredients))
        self._by_name[name.lower()] = recipe_id

    @staticmethod
    def _order(recipes: list[dict]) -> list[dict]:
        return sorted(recipes, key=lambda r: (len(r["ingredients"]), r["id"]))

    # --- Level 1 -----------------------------------------------------------

    def add_recipe(self, recipe_id: str, name: str,
                   ingredients: list[str]) -> bool:
        if recipe_id in self._recipes or name.lower() in self._by_name:
            return False
        self._recipes[recipe_id] = [Version(name, ingredients)]
        self._by_name[name.lower()] = recipe_id
        return True

    def get_recipe(self, recipe_id: str) -> dict | None:
        if recipe_id not in self._recipes:
            return None
        return self._view(recipe_id)

    def update_recipe(self, recipe_id: str, name: str,
                      ingredients: list[str]) -> bool:
        if recipe_id not in self._recipes:
            return False
        if self._name_taken_by_other(name, recipe_id):
            return False
        self._append_version(recipe_id, name, ingredients)
        return True

    def delete_recipe(self, recipe_id: str) -> bool:
        versions = self._recipes.pop(recipe_id, None)
        if versions is None:
            return False
        del self._by_name[versions[-1].name.lower()]
        return True

    # --- Level 2 -----------------------------------------------------------

    def search_recipes(self, query: str) -> list[dict]:
        needle = query.lower()
        return self._order([self._view(recipe_id)
                            for recipe_id, versions in self._recipes.items()
                            if needle in versions[-1].name.lower()])

    def get_all_recipes(self) -> list[dict]:
        return self._order([self._view(recipe_id) for recipe_id in self._recipes])

    # --- Level 3 -----------------------------------------------------------

    def add_user(self, user_id: str, username: str) -> bool:
        if user_id in self._users:
            return False
        self._users[user_id] = username
        return True

    def edit_recipe(self, user_id: str, recipe_id: str, name: str,
                    ingredients: list[str]) -> bool:
        if user_id not in self._users:
            return False
        return self.update_recipe(recipe_id, name, ingredients)

    # --- Level 4 -----------------------------------------------------------

    def get_recipe_history(self, recipe_id: str) -> list[dict] | None:
        versions = self._recipes.get(recipe_id)
        if versions is None:
            return None
        return [{"version": number, "name": version.name,
                 "ingredients": list(version.ingredients)}
                for number, version in enumerate(versions, start=1)]

    def rollback_recipe(self, user_id: str, recipe_id: str,
                        version: int) -> bool:
        if user_id not in self._users or recipe_id not in self._recipes:
            return False
        versions = self._recipes[recipe_id]
        if not 1 <= version <= len(versions):
            return False
        # A rollback is a new version that happens to repeat an old one.
        target = versions[version - 1]
        if self._name_taken_by_other(target.name, recipe_id):
            return False
        self._append_version(recipe_id, target.name, target.ingredients)
        return True
