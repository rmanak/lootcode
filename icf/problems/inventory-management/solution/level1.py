"""Checkpoint: the reference solution after level 1 only."""


class InventoryManager:
    def __init__(self) -> None:
        self._items: dict[str, int] = {}

    def add_item(self, name: str, quantity: int) -> bool:
        if name in self._items:
            return False
        self._items[name] = quantity
        return True

    def copy_item(self, name_from: str, name_to: str) -> bool:
        if name_from not in self._items or name_to in self._items:
            return False
        self._items[name_to] = self._items[name_from]
        return True

    def get_item_quantity(self, name: str) -> int | None:
        return self._items.get(name)
