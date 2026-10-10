"""Checkpoint: the reference solution after levels 1 and 2."""


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

    def find_items(self, prefix: str, suffix: str) -> list[str]:
        matches = sorted((n for n in self._items if n.startswith(prefix) and n.endswith(suffix)),
                         key=lambda n: (-self._items[n], n))
        return [f"{n}({self._items[n]})" for n in matches]
