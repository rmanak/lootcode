"""Checkpoint: the reference solution after level 1 only."""


class Bank:
    def __init__(self) -> None:
        self._balances: dict[str, int] = {}

    def create_account(self, timestamp: int, account_id: str) -> bool:
        if account_id in self._balances:
            return False
        self._balances[account_id] = 0
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
        return self._balances[source_id]
