"""Reference solution — all four levels.

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

    def saved_at(self, timestamp: int) -> "SavedField":
        """This field as a backup entry: a lifetime left, not a moment."""
        remaining = (None if self.expires_at is None
                     else self.expires_at - timestamp)
        return SavedField(self.value, remaining)


@dataclass(slots=True)
class SavedField:
    """A field inside a backup: what was *left* of its life when it was taken."""

    value: str
    remaining: int | None = None

    def restored_at(self, timestamp: int) -> Field:
        """The field again, its remaining lifetime resuming from `timestamp`."""
        expires_at = (None if self.remaining is None
                      else timestamp + self.remaining)
        return Field(self.value, expires_at)


@dataclass(slots=True)
class Backup:
    """Every live field at the moment `backup` was called."""

    taken_at: int
    records: dict[str, dict[str, SavedField]]


class Database:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, Field]] = {}
        self._backups: list[Backup] = []     # appended in timestamp order

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

    # --- Level 4 -----------------------------------------------------------

    def backup(self, timestamp: int) -> int:
        snapshot: dict[str, dict[str, SavedField]] = {}
        for key, fields in self._records.items():
            live = {field: entry.saved_at(timestamp)
                    for field, entry in fields.items()
                    if entry.alive_at(timestamp)}
            if live:
                snapshot[key] = live
        self._backups.append(Backup(timestamp, snapshot))
        return len(snapshot)

    def restore(self, timestamp: int, at_timestamp: int) -> None:
        chosen = None
        for backup in self._backups:
            if backup.taken_at <= at_timestamp:
                chosen = backup
            else:
                break
        if chosen is None:
            return
        # Remaining lifetimes resume from `timestamp`: what was left when the
        # snapshot was taken is what is left now.
        self._records = {
            key: {field: saved.restored_at(timestamp)
                  for field, saved in fields.items()}
            for key, fields in chosen.records.items()
        }
