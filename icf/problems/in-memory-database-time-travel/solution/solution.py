"""Reference solution — all four levels.

The level-1 decision that makes level 4 cheap: **never overwrite, append.**
Every write to a field — a set, a compare-and-set, a delete — appends a
`Version` stamped with the time it happened, carrying the value (or `None` for
a delete) and the moment it expires. The current state is just the last
version, so levels 1-3 read `versions[-1]`; `get_when` binary-searches for the
last version written at or before `at_timestamp` and asks it the same
question, "were you alive then?". A delete or an expired version answers no,
and the search never falls back to an older value.
"""

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

    def scan(self, timestamp: int, key: str) -> list[str]:
        return self._listing(timestamp, key, "")

    def scan_by_prefix(self, timestamp: int, key: str, prefix: str) -> list[str]:
        return self._listing(timestamp, key, prefix)

    # --- Level 3 -----------------------------------------------------------

    def set_with_ttl(self, timestamp: int, key: str, field: str, value: str,
                     ttl: int) -> None:
        self._write(timestamp, key, field, value, timestamp + ttl)

    def compare_and_set_with_ttl(self, timestamp: int, key: str, field: str,
                                 expected_value: str, new_value: str,
                                 ttl: int) -> bool:
        current = self._current(timestamp, key, field)
        if current is None or current.value != expected_value:
            return False
        self._write(timestamp, key, field, new_value, timestamp + ttl)
        return True

    # --- Level 4 -----------------------------------------------------------

    def get_when(self, timestamp: int, key: str, field: str,
                 at_timestamp: int) -> str | None:
        versions = self._records.get(key, {}).get(field, [])
        index = bisect_right([v.written_at for v in versions], at_timestamp)
        if index == 0:
            return None
        version = versions[index - 1]
        return version.value if version.alive_at(at_timestamp) else None
