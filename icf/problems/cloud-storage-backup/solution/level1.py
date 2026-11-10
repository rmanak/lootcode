"""Checkpoint: the reference solution after level 1 only.

The later levels' methods are removed; what remains is enough to pass
levels 1-1 and to fail level 2."""

from dataclasses import dataclass, field

ADMIN = "admin"


@dataclass(slots=True)
class File:
    name: str
    size: int
    owner: str


@dataclass(slots=True)
class User:
    user_id: str
    capacity: int | None            # None means unlimited (the administrator)
    used: int = 0
    backup: dict[str, int] | None = None

    def fits(self, size: int) -> bool:
        return self.capacity is None or self.used + size <= self.capacity

    @property
    def remaining(self) -> int:
        assert self.capacity is not None
        return self.capacity - self.used


class CloudStorage:
    def __init__(self) -> None:
        self._files: dict[str, File] = {}
        self._users: dict[str, User] = {ADMIN: User(ADMIN, None)}

    # --- helpers -----------------------------------------------------------

    def _store(self, name: str, size: int, owner: User) -> None:
        self._files[name] = File(name, size, owner.user_id)
        owner.used += size

    def _remove(self, name: str) -> int:
        removed = self._files.pop(name)
        self._users[removed.owner].used -= removed.size
        return removed.size

    def _regular_user(self, user_id: str) -> User | None:
        """A user that exists and is not the administrator."""
        if user_id == ADMIN:
            return None
        return self._users.get(user_id)

    # --- Level 1 -----------------------------------------------------------

    def add_file(self, name: str, size: int) -> bool:
        if name in self._files:
            return False
        self._store(name, size, self._users[ADMIN])
        return True

    def get_file_size(self, name: str) -> int | None:
        found = self._files.get(name)
        return None if found is None else found.size

    def delete_file(self, name: str) -> int | None:
        if name not in self._files:
            return None
        return self._remove(name)

    def copy_file(self, name_from: str, name_to: str) -> bool:
        source = self._files.get(name_from)
        if source is None or name_to in self._files:
            return False
        owner = self._users[source.owner]
        if not owner.fits(source.size):
            return False
        self._store(name_to, source.size, owner)
        return True

    # --- Level 2 -----------------------------------------------------------

    # --- Level 3 -----------------------------------------------------------

    # --- Level 4 -----------------------------------------------------------

