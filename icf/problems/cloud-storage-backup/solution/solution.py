"""Reference solution — all four levels.

One map holds the whole filesystem: file name -> `File`, and each file names
its owner. A user is a capacity plus a running total of the bytes it owns, so
"does it fit?" is one subtraction rather than a scan. The administrator is a
user too — just one whose capacity is unlimited and who can never be merged,
backed up or restored — which keeps `add_file` and `add_file_by` the same code.

A backup is a frozen copy of {name: size}. Restoring is "delete what the user
has, re-create what the backup has, skip what someone else now owns".
"""

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

    def get_n_largest(self, prefix: str, n: int) -> list[str]:
        matching = [f for f in self._files.values() if f.name.startswith(prefix)]
        matching.sort(key=lambda f: (-f.size, f.name))
        return [f"{f.name}({f.size})" for f in matching[:n]]

    # --- Level 3 -----------------------------------------------------------

    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self._users:
            return False
        self._users[user_id] = User(user_id, capacity)
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        user = self._regular_user(user_id)
        if user is None or name in self._files or not user.fits(size):
            return None
        self._store(name, size, user)
        return user.remaining

    def merge_user(self, user_id_1: str, user_id_2: str) -> int | None:
        if user_id_1 == user_id_2:
            return None
        first = self._regular_user(user_id_1)
        second = self._regular_user(user_id_2)
        if first is None or second is None:
            return None
        assert first.capacity is not None and second.capacity is not None
        for f in self._files.values():
            if f.owner == second.user_id:
                f.owner = first.user_id
        first.capacity += second.capacity
        first.used += second.used
        del self._users[user_id_2]          # its backup goes with it
        return first.remaining

    # --- Level 4 -----------------------------------------------------------

    def backup_user(self, user_id: str) -> int | None:
        user = self._regular_user(user_id)
        if user is None:
            return None
        user.backup = {f.name: f.size for f in self._files.values()
                       if f.owner == user_id}
        return len(user.backup)

    def restore_user(self, user_id: str) -> int | None:
        user = self._regular_user(user_id)
        if user is None:
            return None
        for name in [f.name for f in self._files.values() if f.owner == user_id]:
            self._remove(name)
        restored = 0
        for name, size in sorted((user.backup or {}).items()):
            if name in self._files:          # someone else holds the name now
                continue
            self._store(name, size, user)
            restored += 1
        return restored
