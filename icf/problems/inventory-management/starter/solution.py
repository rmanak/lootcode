class InventoryManager:
    """A shared warehouse inventory.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: items ---------------------------------------------------

    def add_item(self, name: str, quantity: int) -> bool:
        pass

    def copy_item(self, name_from: str, name_to: str) -> bool:
        pass

    def get_item_quantity(self, name: str) -> int | None:
        pass

    # --- Level 2: finding items -------------------------------------------

    def find_items(self, prefix: str, suffix: str) -> list[str]:
        pass

    # --- Level 3: users and capacity --------------------------------------

    def add_user(self, user_id: str, capacity: int) -> bool:
        pass

    def add_item_by(self, user_id: str, name: str, quantity: int) -> int | None:
        pass

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        pass

    # --- Level 4: packing items -------------------------------------------

    def pack_item(self, user_id: str, name: str) -> int | None:
        pass

    def unpack_item(self, user_id: str, name: str) -> int | None:
        pass
