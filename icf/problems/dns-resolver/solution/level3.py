"""Checkpoint: the reference solution after level 3 only.

The later levels' methods are removed; what remains is enough to pass
levels 1-3 and to fail level 4."""

from dataclasses import dataclass, field

RESOLVED, NOT_FOUND, LOOP = "RESOLVED", "NOT_FOUND", "LOOP"


def normalize(name: str) -> str:
    """Names are case-insensitive, and one trailing dot is ignored."""
    name = name.lower()
    return name[:-1] if name.endswith(".") else name


@dataclass(frozen=True, slots=True)
class Record:
    """An address record (`data` is an IP) or an alias (`data` is a name)."""

    data: str
    expires_at: int | None = None

    def alive_at(self, timestamp: int) -> bool:
        return self.expires_at is None or timestamp < self.expires_at


@dataclass(slots=True)
class Outcome:
    status: str
    addresses: list[str] = field(default_factory=list)
    used: list[Record] = field(default_factory=list)   # the records behind the answer


class Resolver:
    def __init__(self) -> None:
        self._addresses: dict[str, list[Record]] = {}
        self._aliases: dict[str, Record] = {}
        self._fallbacks: dict[str, list[str]] = {}

    # --- lookups at a moment ------------------------------------------------

    def _live_addresses(self, timestamp: int, name: str) -> list[Record]:
        return [r for r in self._addresses.get(name, []) if r.alive_at(timestamp)]

    def _live_alias(self, timestamp: int, name: str) -> Record | None:
        alias = self._aliases.get(name)
        return alias if alias is not None and alias.alive_at(timestamp) else None

    def _walk(self, timestamp: int, name: str) -> tuple[list[str], list[Record], bool]:
        """Follow aliases from `name`: (names visited, aliases used, looped?)."""
        chain, used, seen = [name], [], {name}
        while (alias := self._live_alias(timestamp, chain[-1])) is not None:
            used.append(alias)
            chain.append(alias.data)
            if alias.data in seen:
                return chain, used, True
            seen.add(alias.data)
        return chain, used, False

    def _resolve(self, timestamp: int, name: str, attempted: set[str]) -> Outcome:
        attempted.add(name)
        chain, aliases, looped = self._walk(timestamp, name)
        if looped:
            return Outcome(LOOP)
        records = self._live_addresses(timestamp, chain[-1])
        if records:
            return Outcome(RESOLVED, [r.data for r in records], aliases + records)
        for fallback in self._fallbacks.get(name, []):
            if fallback in attempted:
                continue
            outcome = self._resolve(timestamp, fallback, attempted)
            if outcome.status != NOT_FOUND:      # an answer, or a loop: stop here
                return outcome
        return Outcome(NOT_FOUND)

    def _add_address(self, timestamp: int, name: str, ip: str,
                     expires_at: int | None) -> bool:
        name = normalize(name)
        live = self._live_addresses(timestamp, name)
        if self._live_alias(timestamp, name) is not None or any(r.data == ip for r in live):
            return False
        self._addresses[name] = live + [Record(ip, expires_at)]
        return True

    def _add_alias(self, timestamp: int, name: str, target: str,
                   expires_at: int | None) -> bool:
        name, target = normalize(name), normalize(target)
        if name == target or self._live_alias(timestamp, name) is not None:
            return False
        if self._live_addresses(timestamp, name):
            return False
        self._aliases[name] = Record(target, expires_at)
        return True

    # --- Level 1 -----------------------------------------------------------

    def add_record(self, timestamp: int, name: str, ip: str) -> bool:
        return self._add_address(timestamp, name, ip, None)

    def remove_record(self, timestamp: int, name: str, ip: str) -> bool:
        name = normalize(name)
        live = self._live_addresses(timestamp, name)
        kept = [r for r in live if r.data != ip]
        if len(kept) == len(live):
            return False
        self._addresses[name] = kept
        return True

    def resolve(self, timestamp: int, name: str) -> list[str] | None:
        outcome = self._resolve(timestamp, normalize(name), set())
        return outcome.addresses if outcome.status == RESOLVED else None

    # --- Level 2 -----------------------------------------------------------

    def add_alias(self, timestamp: int, name: str, target: str) -> bool:
        return self._add_alias(timestamp, name, target, None)

    def remove_alias(self, timestamp: int, name: str) -> bool:
        name = normalize(name)
        if self._live_alias(timestamp, name) is None:
            return False
        del self._aliases[name]
        return True

    def get_chain(self, timestamp: int, name: str) -> list[str]:
        return self._walk(timestamp, normalize(name))[0]

    # --- Level 3 -----------------------------------------------------------

    def add_fallback(self, timestamp: int, name: str, fallback: str) -> bool:
        name, fallback = normalize(name), normalize(fallback)
        fallbacks = self._fallbacks.setdefault(name, [])
        if name == fallback or fallback in fallbacks:
            return False
        fallbacks.append(fallback)
        return True

    def get_status(self, timestamp: int, name: str) -> str:
        return self._resolve(timestamp, normalize(name), set()).status

    # --- Level 4 -----------------------------------------------------------

