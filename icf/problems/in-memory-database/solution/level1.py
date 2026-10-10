"""Checkpoint: the reference solution as it stands after level 1 only.

Used by icf/scripts/verify_icf.py to prove that level 2 really does ask for
something level 1 did not — level 2's tests must fail against this.
"""


class Database:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, str]] = {}

    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        self._records.setdefault(key, {})[field] = value

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        return self._records.get(key, {}).get(field)

    def delete(self, timestamp: int, key: str, field: str) -> bool:
        if field not in self._records.get(key, {}):
            return False
        del self._records[key][field]
        return True

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected: str, new_value: str) -> bool:
        if self._records.get(key, {}).get(field) != expected:
            return False
        if field not in self._records.get(key, {}):
            return False
        self._records[key][field] = new_value
        return True
