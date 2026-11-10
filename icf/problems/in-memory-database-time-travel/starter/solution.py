class Database:
    """An in-memory key/field store that remembers its past.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: records and conditional writes --------------------------

    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        pass

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        pass

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected_value: str, new_value: str) -> bool:
        pass

    def compare_and_delete(self, timestamp: int, key: str, field: str,
                           expected_value: str) -> bool:
        pass

    # --- Level 2: scanning a record ---------------------------------------

    def scan(self, timestamp: int, key: str) -> list[str]:
        pass

    def scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> list[str]:
        pass

    # --- Level 3: fields that expire --------------------------------------

    def set_with_ttl(self, timestamp: int, key: str, field: str, value: str,
                     ttl: int) -> None:
        pass

    def compare_and_set_with_ttl(self, timestamp: int, key: str, field: str,
                                 expected_value: str, new_value: str,
                                 ttl: int) -> bool:
        pass

    # --- Level 4: reading the past ----------------------------------------

    def get_when(self, timestamp: int, key: str, field: str,
                 at_timestamp: int) -> str | None:
        pass
