"""Checkpoint: the reference solution after levels 1-2 (no payments yet)."""


class Bank:
    def __init__(self) -> None:
        self._balances: dict[str, int] = {}
        self._outgoing: dict[str, int] = {}

    def create_account(self, timestamp: int, account_id: str) -> bool:
        if account_id in self._balances:
            return False
        self._balances[account_id] = 0
        self._outgoing[account_id] = 0
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        if account_id not in self._balances:
            return None
        self._balances[account_id] += amount
        return self._balances[account_id]

    def transfer(self, timestamp: int, source_id: str, target_id: str,
                 amount: int) -> int | None:
        if source_id not in self._balances or target_id not in self._balances:
            return None
        if source_id == target_id or self._balances[source_id] < amount:
            return None
        self._balances[source_id] -= amount
        self._balances[target_id] += amount
        self._outgoing[source_id] += amount
        return self._balances[source_id]

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        ranked = sorted(self._outgoing.items(), key=lambda kv: (-kv[1], kv[0]))
        return [f"{account_id}({total})" for account_id, total in ranked[:n]]
