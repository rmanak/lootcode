"""Reference solution — all four levels.

Two choices carry the whole thing:

* **Every file has an owner from level 1 on.** Files added with `add_file`
  belong to "admin", whose capacity is simply unlimited — so level 3 does not
  have to special-case the files that were already there, and `copy_file` only
  has to carry the owner across.
* **Each user's used bytes are a running total**, kept correct by the two
  helpers every add, copy, removal, compression and decompression goes
  through. A capacity check is then one comparison, and compressing a file is
  just a drop followed by a put.

Directories need no representation at all: they only exist as parts of file
names, so a directory name is simply a name with no file behind it.
"""

from dataclasses import dataclass

ADMIN = "admin"
COMPRESSED = ".COMPRESSED"


@dataclass(slots=True)
class File:
    size: int
    owner: str


@dataclass(slots=True)
class User:
    capacity: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return self.capacity - self.used


class CloudStorage:
    def __init__(self) -> None:
        self._files: dict[str, File] = {}
        #: Everyone except "admin", whose capacity is unlimited.
        self._users: dict[str, User] = {}

    # --- helpers -----------------------------------------------------------

    def _fits(self, owner: str, extra: int) -> bool:
        if owner == ADMIN:
            return True
        user = self._users[owner]
        return user.used + extra <= user.capacity

    def _put(self, name: str, size: int, owner: str) -> None:
        self._files[name] = File(size, owner)
        if owner != ADMIN:
            self._users[owner].used += size

    def _drop(self, name: str) -> File:
        file = self._files.pop(name)
        if file.owner != ADMIN:
            self._users[file.owner].used -= file.size
        return file

    def _owned_by(self, user_id: str, name: str) -> File | None:
        file = self._files.get(name)
        if user_id not in self._users or file is None or file.owner != user_id:
            return None
        return file

    # --- Level 1 -----------------------------------------------------------

    def add_file(self, name: str, size: int) -> bool:
        if name in self._files:
            return False
        self._put(name, size, ADMIN)
        return True

    def copy_file(self, name_from: str, name_to: str) -> bool:
        source = self._files.get(name_from)
        if source is None or name_to in self._files:
            return False
        if not self._fits(source.owner, source.size):
            return False
        self._put(name_to, source.size, source.owner)
        return True

    def get_file_size(self, name: str) -> int | None:
        file = self._files.get(name)
        return None if file is None else file.size

    # --- Level 2 -----------------------------------------------------------

    def find_file(self, prefix: str, suffix: str) -> list[str]:
        matches = sorted(((name, file) for name, file in self._files.items()
                          if name.startswith(prefix) and name.endswith(suffix)),
                         key=lambda match: (-match[1].size, match[0]))
        return [f"{name}({file.size})" for name, file in matches]

    # --- Level 3 -----------------------------------------------------------

    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self._users:
            return False
        self._users[user_id] = User(capacity)
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        if user_id not in self._users or name in self._files:
            return None
        if not self._fits(user_id, size):
            return None
        self._put(name, size, user_id)
        return self._users[user_id].remaining

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        user = self._users.get(user_id)
        if user is None:
            return None
        user.capacity = capacity
        # Biggest first, breaking ties by name, until what is left fits.
        owned = sorted(((name, file) for name, file in self._files.items()
                        if file.owner == user_id),
                       key=lambda match: (-match[1].size, match[0]))
        removed = 0
        for name, _file in owned:
            if user.used <= capacity:
                break
            self._drop(name)
            removed += 1
        return removed

    # --- Level 4 -----------------------------------------------------------

    def compress_file(self, user_id: str, name: str) -> int | None:
        file = self._owned_by(user_id, name)
        if file is None or name + COMPRESSED in self._files:
            return None
        self._drop(name)
        self._put(name + COMPRESSED, file.size // 2, user_id)
        return self._users[user_id].remaining

    def decompress_file(self, user_id: str, name: str) -> int | None:
        file = self._owned_by(user_id, name)
        if file is None or not name.endswith(COMPRESSED):
            return None
        original = name[:-len(COMPRESSED)]
        if original in self._files:
            return None
        # Decompressing grows the owner's total by exactly the compressed size.
        if not self._fits(user_id, file.size):
            return None
        self._drop(name)
        self._put(original, file.size * 2, user_id)
        return self._users[user_id].remaining
