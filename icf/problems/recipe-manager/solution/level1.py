"""Checkpoint: the reference solution after level 1 only.

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
