"""Checkpoint: the reference solution after levels 1 and 2."""


class CloudStorage:
    def __init__(self) -> None:
        self._sizes: dict[str, int] = {}

    def add_file(self, name: str, size: int) -> bool:
        if name in self._sizes:
            return False
        self._sizes[name] = size
        return True

    def copy_file(self, name_from: str, name_to: str) -> bool:
        if name_from not in self._sizes or name_to in self._sizes:
            return False
        self._sizes[name_to] = self._sizes[name_from]
        return True

    def get_file_size(self, name: str) -> int | None:
        return self._sizes.get(name)

    def find_file(self, prefix: str, suffix: str) -> list[str]:
        matches = sorted((n for n in self._sizes if n.startswith(prefix) and n.endswith(suffix)),
                         key=lambda n: (-self._sizes[n], n))
        return [f"{n}({self._sizes[n]})" for n in matches]
