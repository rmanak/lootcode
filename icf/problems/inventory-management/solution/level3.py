"""Checkpoint: the reference solution after levels 1 to 3."""

from dataclasses import dataclass

ADMIN = "admin"


@dataclass(slots=True)
class Item:
    quantity: int
    owner: str


class InventoryManager:
    def __init__(self) -> None:
        self._items: dict[str, Item] = {}
        self._capacity: dict[str, int] = {}

    def _used(self, user_id: str) -> int:
        return sum(item.quantity for item in self._items.values()
                   if item.owner == user_id)

    def add_item(self, name: str, quantity: int) -> bool:
        if name in self._items:
            return False
        self._items[name] = Item(quantity, ADMIN)
        return True

    def copy_item(self, name_from: str, name_to: str) -> bool:
        source = self._items.get(name_from)
        if source is None or name_to in self._items:
            return False
        if (source.owner != ADMIN
                and self._used(source.owner) + source.quantity > self._capacity[source.owner]):
            return False
        self._items[name_to] = Item(source.quantity, source.owner)
        return True

    def get_item_quantity(self, name: str) -> int | None:
        item = self._items.get(name)
        return None if item is None else item.quantity

    def find_items(self, prefix: str, suffix: str) -> list[str]:
        matches = sorted(((name, item) for name, item in self._items.items()
                          if name.startswith(prefix) and name.endswith(suffix)),
                         key=lambda match: (-match[1].quantity, match[0]))
        return [f"{name}({item.quantity})" for name, item in matches]

    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self._capacity:
            return False
        self._capacity[user_id] = capacity
        return True

    def add_item_by(self, user_id: str, name: str, quantity: int) -> int | None:
        if user_id not in self._capacity or name in self._items:
            return None
        if self._used(user_id) + quantity > self._capacity[user_id]:
            return None
        self._items[name] = Item(quantity, user_id)
        return self._capacity[user_id] - self._used(user_id)

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        if user_id not in self._capacity:
            return None
        self._capacity[user_id] = capacity
        owned = sorted(((name, item) for name, item in self._items.items()
                        if item.owner == user_id),
                       key=lambda match: (-match[1].quantity, match[0]))
        removed = 0
        for name, _item in owned:
            if self._used(user_id) <= capacity:
                break
            del self._items[name]
            removed += 1
        return removed
