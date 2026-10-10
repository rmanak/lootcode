"""Checkpoint: the reference solution after levels 1 to 3."""

from dataclasses import dataclass

ADMIN = "admin"


@dataclass(slots=True)
class File:
    size: int
    owner: str


class CloudStorage:
    def __init__(self) -> None:
        self._files: dict[str, File] = {}
        self._capacity: dict[str, int] = {}

    def _used(self, user_id: str) -> int:
        return sum(file.size for file in self._files.values()
                   if file.owner == user_id)

    def add_file(self, name: str, size: int) -> bool:
        if name in self._files:
            return False
        self._files[name] = File(size, ADMIN)
        return True

    def copy_file(self, name_from: str, name_to: str) -> bool:
        source = self._files.get(name_from)
        if source is None or name_to in self._files:
            return False
        if (source.owner != ADMIN
                and self._used(source.owner) + source.size > self._capacity[source.owner]):
            return False
        self._files[name_to] = File(source.size, source.owner)
        return True

    def get_file_size(self, name: str) -> int | None:
        file = self._files.get(name)
        return None if file is None else file.size

    def find_file(self, prefix: str, suffix: str) -> list[str]:
        matches = sorted(((name, file) for name, file in self._files.items()
                          if name.startswith(prefix) and name.endswith(suffix)),
                         key=lambda match: (-match[1].size, match[0]))
        return [f"{name}({file.size})" for name, file in matches]

    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self._capacity:
            return False
        self._capacity[user_id] = capacity
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        if user_id not in self._capacity or name in self._files:
            return None
        if self._used(user_id) + size > self._capacity[user_id]:
            return None
        self._files[name] = File(size, user_id)
        return self._capacity[user_id] - self._used(user_id)

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        if user_id not in self._capacity:
            return None
        self._capacity[user_id] = capacity
        owned = sorted(((name, file) for name, file in self._files.items()
                        if file.owner == user_id),
                       key=lambda match: (-match[1].size, match[0]))
        removed = 0
        for name, _file in owned:
            if self._used(user_id) <= capacity:
                break
            del self._files[name]
            removed += 1
        return removed
