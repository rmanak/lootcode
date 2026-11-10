"""Checkpoint: the reference solution after level 1 only.

The later levels' methods are removed; what remains is enough to pass
levels 1-1 and to fail level 2."""

from bisect import bisect_right
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Version:
    """One write to a field: what it held from `written_at` on."""

    written_at: int
    value: str | None            # None records a delete
    expires_at: int | None = None

    def alive_at(self, timestamp: int) -> bool:
        return self.value is not None and (self.expires_at is None
                                           or timestamp < self.expires_at)


class Database:
    def __init__(self) -> None:
        # key -> field -> versions, oldest first
        self._records: dict[str, dict[str, list[Version]]] = {}

    # --- helpers -----------------------------------------------------------

    def _versions(self, key: str, field: str) -> list[Version]:
        return self._records.setdefault(key, {}).setdefault(field, [])

    def _current(self, timestamp: int, key: str, field: str) -> Version | None:
        """The field's live version at `timestamp`, or None."""
        versions = self._records.get(key, {}).get(field)
        if not versions or not versions[-1].alive_at(timestamp):
            return None
        return versions[-1]

    def _write(self, timestamp: int, key: str, field: str, value: str | None,
               expires_at: int | None) -> None:
        self._versions(key, field).append(Version(timestamp, value, expires_at))

    def _listing(self, timestamp: int, key: str, prefix: str) -> list[str]:
        fields = self._records.get(key, {})
        return [f"{name}({versions[-1].value})"
                for name, versions in sorted(fields.items())
                if name.startswith(prefix) and versions[-1].alive_at(timestamp)]

    # --- Level 1 -----------------------------------------------------------

    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        self._write(timestamp, key, field, value, None)

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        current = self._current(timestamp, key, field)
        return None if current is None else current.value

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected_value: str, new_value: str) -> bool:
        current = self._current(timestamp, key, field)
        if current is None or current.value != expected_value:
            return False
        # the value changes, the lifetime does not
        self._write(timestamp, key, field, new_value, current.expires_at)
        return True

    def compare_and_delete(self, timestamp: int, key: str, field: str,
                           expected_value: str) -> bool:
        current = self._current(timestamp, key, field)
        if current is None or current.value != expected_value:
            return False
        self._write(timestamp, key, field, None, None)
        return True

    # --- Level 2 -----------------------------------------------------------

    # --- Level 3 -----------------------------------------------------------

    # --- Level 4 -----------------------------------------------------------

