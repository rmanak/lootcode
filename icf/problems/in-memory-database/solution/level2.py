"""Checkpoint: the reference solution after levels 1–2 (no lifetimes yet)."""


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
        record = self._records.get(key, {})
        if field not in record or record[field] != expected:
            return False
        record[field] = new_value
        return True

    def scan(self, timestamp: int, key: str) -> str:
        return self._render(sorted(self._records.get(key, {}).items()))

    def scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> str:
        return self._render([(f, v) for f, v in sorted(
            self._records.get(key, {}).items()) if f.startswith(prefix)])

    @staticmethod
    def _render(pairs) -> str:
        return ", ".join(f"{field}({value})" for field, value in pairs)
