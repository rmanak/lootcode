"""Checkpoint: the reference solution after levels 1-3 (no backups yet).

The data model is one dict of records, each a dict of field name to a
``Field`` — a value plus the moment it expires, where ``None`` means
permanent. That single optional expiry is what makes levels 3 and 4 small:
expiry is one predicate applied at read time, and a backup is the same
structure with the absolute expiry rewritten as a *remaining* lifetime.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Field:
    """One field's value. `expires_at` of None means it never expires."""

    value: str
    expires_at: int | None = None

    def alive_at(self, timestamp: int) -> bool:
        return self.expires_at is None or timestamp < self.expires_at


class Database:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, Field]] = {}

    # --- helpers -----------------------------------------------------------

    def _live_field(self, timestamp: int, key: str, field: str) -> Field | None:
        entry = self._records.get(key, {}).get(field)
        if entry is None or not entry.alive_at(timestamp):
            return None
        return entry

    def _live_fields(self, timestamp: int, key: str) -> list[tuple[str, Field]]:
        return sorted(((field, entry)
                       for field, entry in self._records.get(key, {}).items()
                       if entry.alive_at(timestamp)),
                      key=lambda item: item[0])

    @staticmethod
    def _format(entries: list[tuple[str, Field]]) -> str:
        return ", ".join(f"{field}({entry.value})" for field, entry in entries)

    # --- Level 1 -----------------------------------------------------------

    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        # A plain set clears any lifetime the field had (level 3).
        self._records.setdefault(key, {})[field] = Field(value)

    def get(self, timestamp: int, key: str, field: str) -> str | None:
        entry = self._live_field(timestamp, key, field)
        return None if entry is None else entry.value

    def delete(self, timestamp: int, key: str, field: str) -> bool:
        if self._live_field(timestamp, key, field) is None:
            return False
        del self._records[key][field]
        return True

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected: str, new_value: str) -> bool:
        entry = self._live_field(timestamp, key, field)
        if entry is None or entry.value != expected:
            return False
        # An update in place, not a re-set: the existing expiry stays.
        entry.value = new_value
        return True

    # --- Level 2 -----------------------------------------------------------

    def scan(self, timestamp: int, key: str) -> str:
        return self._format(self._live_fields(timestamp, key))

    def scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> str:
        return self._format([(field, entry)
                             for field, entry in self._live_fields(timestamp, key)
                             if field.startswith(prefix)])

    # --- Level 3 -----------------------------------------------------------

    def set_with_ttl(self, timestamp: int, key: str, field: str, value: str,
                     ttl: int) -> None:
        self._records.setdefault(key, {})[field] = Field(value, timestamp + ttl)
