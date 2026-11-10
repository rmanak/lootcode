class CloudStorage:
    """A shared cloud filesystem with per-user capacities and backups.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: files ---------------------------------------------------

    def add_file(self, name: str, size: int) -> bool:
        pass

    def get_file_size(self, name: str) -> int | None:
        pass

    def delete_file(self, name: str) -> int | None:
        pass

    def copy_file(self, name_from: str, name_to: str) -> bool:
        pass

    # --- Level 2: the largest files ---------------------------------------

    def get_n_largest(self, prefix: str, n: int) -> list[str]:
        pass

    # --- Level 3: users, capacity and merging -----------------------------

    def add_user(self, user_id: str, capacity: int) -> bool:
        pass

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        pass

    def merge_user(self, user_id_1: str, user_id_2: str) -> int | None:
        pass

    # --- Level 4: backup and restore --------------------------------------

    def backup_user(self, user_id: str) -> int | None:
        pass

    def restore_user(self, user_id: str) -> int | None:
        pass
