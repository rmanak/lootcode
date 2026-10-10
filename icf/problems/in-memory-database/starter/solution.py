class Database:
    """An in-memory key/field store.

    Implement the methods for the level you are on; the ones for later levels
    are already declared so the class stays importable. Your code carries
    forward between levels — extend it rather than starting again.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: records and fields --------------------------------------

    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        pass

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        pass

    def delete(self, timestamp: int, key: str, field: str) -> bool:
        pass

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected: str, new_value: str) -> bool:
        pass

    # --- Level 2: scanning a record ---------------------------------------

    def scan(self, timestamp: int, key: str) -> str:
        pass

    def scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> str:
        pass

    # --- Level 3: fields that expire --------------------------------------

    def set_with_ttl(self, timestamp: int, key: str, field: str, value: str,
                     ttl: int) -> None:
        pass

    # --- Level 4: backup and restore --------------------------------------

    def backup(self, timestamp: int) -> int:
        pass

    def restore(self, timestamp: int, at_timestamp: int) -> None:
        pass
