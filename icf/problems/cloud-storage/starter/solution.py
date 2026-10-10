class CloudStorage:
    """An in-memory catalogue of files and their metainformation.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: files ---------------------------------------------------

    def add_file(self, name: str, size: int) -> bool:
        pass

    def copy_file(self, name_from: str, name_to: str) -> bool:
        pass

    def get_file_size(self, name: str) -> int | None:
        pass

    # --- Level 2: finding files -------------------------------------------

    def find_file(self, prefix: str, suffix: str) -> list[str]:
        pass

    # --- Level 3: users and capacity --------------------------------------

    def add_user(self, user_id: str, capacity: int) -> bool:
        pass

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        pass

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        pass

    # --- Level 4: compression ---------------------------------------------

    def compress_file(self, user_id: str, name: str) -> int | None:
        pass

    def decompress_file(self, user_id: str, name: str) -> int | None:
        pass
