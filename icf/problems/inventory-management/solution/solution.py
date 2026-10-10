"""Reference solution — all four levels.

Two choices carry the whole thing:

* **Every item has an owner from level 1 on.** Items added with `add_item`
  belong to "admin", whose capacity is simply unlimited — so level 3 does not
  have to special-case the old items, and `copy_item` only has to carry the
  owner across.
* **Each user's used units are a running total**, updated by every add, copy,
  removal, pack and unpack through the same two helpers. A capacity check is
  then one comparison, and packing is just a drop followed by a put.
"""

from dataclasses import dataclass

ADMIN = "admin"
PACKED = ".packed"


@dataclass(slots=True)
class Item:
    quantity: int
    owner: str


@dataclass(slots=True)
class User:
    capacity: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return self.capacity - self.used


class InventoryManager:
    def __init__(self) -> None:
        self._items: dict[str, Item] = {}
        #: Everyone except "admin", whose capacity is unlimited.
        self._users: dict[str, User] = {}

    # --- helpers -----------------------------------------------------------

    def _fits(self, owner: str, extra: int) -> bool:
        if owner == ADMIN:
            return True
        user = self._users[owner]
        return user.used + extra <= user.capacity

    def _put(self, name: str, quantity: int, owner: str) -> None:
        self._items[name] = Item(quantity, owner)
        if owner != ADMIN:
            self._users[owner].used += quantity

    def _drop(self, name: str) -> Item:
        item = self._items.pop(name)
        if item.owner != ADMIN:
            self._users[item.owner].used -= item.quantity
        return item

    def _owned_by(self, user_id: str, name: str) -> Item | None:
        item = self._items.get(name)
        if user_id not in self._users or item is None or item.owner != user_id:
            return None
        return item

    # --- Level 1 -----------------------------------------------------------

    def add_item(self, name: str, quantity: int) -> bool:
        if name in self._items:
            return False
        self._put(name, quantity, ADMIN)
        return True

    def copy_item(self, name_from: str, name_to: str) -> bool:
        source = self._items.get(name_from)
        if source is None or name_to in self._items:
            return False
        if not self._fits(source.owner, source.quantity):
            return False
        self._put(name_to, source.quantity, source.owner)
        return True

    def get_item_quantity(self, name: str) -> int | None:
        item = self._items.get(name)
        return None if item is None else item.quantity

    # --- Level 2 -----------------------------------------------------------

    def find_items(self, prefix: str, suffix: str) -> list[str]:
        matches = sorted(((name, item) for name, item in self._items.items()
                          if name.startswith(prefix) and name.endswith(suffix)),
                         key=lambda match: (-match[1].quantity, match[0]))
        return [f"{name}({item.quantity})" for name, item in matches]

    # --- Level 3 -----------------------------------------------------------

    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self._users:
            return False
        self._users[user_id] = User(capacity)
        return True

    def add_item_by(self, user_id: str, name: str, quantity: int) -> int | None:
        if user_id not in self._users or name in self._items:
            return None
        if not self._fits(user_id, quantity):
            return None
        self._put(name, quantity, user_id)
        return self._users[user_id].remaining

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        user = self._users.get(user_id)
        if user is None:
            return None
        user.capacity = capacity
        # Biggest first, breaking ties by name, until what is left fits.
        owned = sorted(((name, item) for name, item in self._items.items()
                        if item.owner == user_id),
                       key=lambda match: (-match[1].quantity, match[0]))
        removed = 0
        for name, _item in owned:
            if user.used <= capacity:
                break
            self._drop(name)
            removed += 1
        return removed

    # --- Level 4 -----------------------------------------------------------

    def pack_item(self, user_id: str, name: str) -> int | None:
        item = self._owned_by(user_id, name)
        if item is None:
            return None
        if name.endswith(PACKED) or name + PACKED in self._items:
            return None
        self._drop(name)
        self._put(name + PACKED, item.quantity // 2, user_id)
        return self._users[user_id].remaining

    def unpack_item(self, user_id: str, name: str) -> int | None:
        packed = self._owned_by(user_id, name + PACKED)
        if packed is None or name in self._items:
            return None
        # Unpacking grows the user's total by exactly the packed quantity.
        if not self._fits(user_id, packed.quantity):
            return None
        self._drop(name + PACKED)
        self._put(name, packed.quantity * 2, user_id)
        return self._users[user_id].remaining
