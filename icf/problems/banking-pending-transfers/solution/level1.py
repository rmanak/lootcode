"""Checkpoint: the reference solution after level 1 only.

The later levels' methods are removed; what remains is enough to pass
levels 1-1 and to fail level 2."""

from dataclasses import dataclass, field

DAY_MS = 86_400_000


@dataclass(frozen=True, slots=True)
class Entry:
    sequence: int
    timestamp: int
    kind: str           # deposit | withdraw | transfer_out | transfer_in
    amount: int

    def __str__(self) -> str:
        return f"{self.timestamp}:{self.kind}:{self.amount}"


@dataclass(slots=True, eq=False)     # an account is an identity, not a value
class Account:
    account_id: str
    balance: int = 0
    activity: int = 0
    history: list[Entry] = field(default_factory=list)
    merged_into: "Account | None" = None


@dataclass(slots=True)
class PendingTransfer:
    transfer_id: str
    source: Account
    target: Account
    amount: int
    expires_at: int
    status: str = "PENDING"     # PENDING | ACCEPTED | EXPIRED | CANCELED


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}
        self._transfers: dict[str, PendingTransfer] = {}
        self._sequence = 0

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def _resolve(account: Account) -> Account:
        while account.merged_into is not None:
            account = account.merged_into
        return account

    def _record(self, account: Account, timestamp: int, kind: str,
                amount: int) -> None:
        self._sequence += 1
        account.history.append(Entry(self._sequence, timestamp, kind, amount))
        account.activity += amount

    def _expire(self, timestamp: int) -> None:
        """Return the held money of every transfer that ran out of time."""
        for transfer in self._transfers.values():
            if transfer.status == "PENDING" and transfer.expires_at <= timestamp:
                transfer.status = "EXPIRED"
                self._resolve(transfer.source).balance += transfer.amount

    def _complete_transfer(self, timestamp: int, source: Account,
                           target: Account, amount: int) -> None:
        target.balance += amount
        self._record(source, timestamp, "transfer_out", amount)
        self._record(target, timestamp, "transfer_in", amount)

    # --- Level 1 -----------------------------------------------------------

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._expire(timestamp)
        if account_id in self._accounts:
            return False
        self._accounts[account_id] = Account(account_id)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._expire(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        account.balance += amount
        self._record(account, timestamp, "deposit", amount)
        return account.balance

    def withdraw(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._expire(timestamp)
        account = self._accounts.get(account_id)
        if account is None or account.balance < amount:
            return None
        account.balance -= amount
        self._record(account, timestamp, "withdraw", amount)
        return account.balance

    def get_balance(self, timestamp: int, account_id: str) -> int | None:
        self._expire(timestamp)
        account = self._accounts.get(account_id)
        return None if account is None else account.balance

    # --- Level 2 -----------------------------------------------------------

    # --- Level 3 -----------------------------------------------------------

    # --- Level 4 -----------------------------------------------------------

