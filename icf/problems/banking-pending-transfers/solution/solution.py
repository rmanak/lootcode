"""Reference solution — all four levels.

* **A completed transaction is a record, written once.** Every deposit,
  withdrawal and completed transfer appends an `Entry` to each account it
  touches, stamped with a bank-wide sequence number. An account's activity is
  the sum of its entries, and a merge is "concatenate, then sort by sequence" —
  so history needs nothing at level 4 that level 1 didn't already record.
* **A pending transfer holds an account object, not an id.** Money leaves the
  source when the transfer is initiated; the transfer remembers the source and
  target *accounts*. Merges are followed through `merged_into`, so a refund or
  an acceptance finds the account that owns the money now, and a re-created id
  (a new object) can never accept or receive what belonged to the old one.
"""

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

    def transfer(self, timestamp: int, source_id: str, target_id: str,
                 amount: int) -> int | None:
        self._expire(timestamp)
        source = self._accounts.get(source_id)
        target = self._accounts.get(target_id)
        if source is None or target is None or source is target:
            return None
        if source.balance < amount:
            return None
        source.balance -= amount
        self._complete_transfer(timestamp, source, target, amount)
        return source.balance

    def top_activity(self, timestamp: int, n: int) -> list[str]:
        self._expire(timestamp)
        ranked = sorted(self._accounts.values(),
                        key=lambda account: (-account.activity, account.account_id))
        return [f"{account.account_id}({account.activity})"
                for account in ranked[:n]]

    # --- Level 3 -----------------------------------------------------------

    def initiate_transfer(self, timestamp: int, source_id: str, target_id: str,
                          amount: int) -> str | None:
        self._expire(timestamp)
        source = self._accounts.get(source_id)
        target = self._accounts.get(target_id)
        if source is None or target is None or source is target:
            return None
        if source.balance < amount:
            return None
        source.balance -= amount                      # held until accepted
        transfer_id = f"transfer{len(self._transfers) + 1}"
        self._transfers[transfer_id] = PendingTransfer(
            transfer_id, source, target, amount, timestamp + DAY_MS)
        return transfer_id

    def accept_transfer(self, timestamp: int, account_id: str,
                        transfer_id: str) -> bool:
        self._expire(timestamp)
        account = self._accounts.get(account_id)
        transfer = self._transfers.get(transfer_id)
        if account is None or transfer is None or transfer.status != "PENDING":
            return False
        if self._resolve(transfer.target) is not account:
            return False
        transfer.status = "ACCEPTED"
        self._complete_transfer(timestamp, self._resolve(transfer.source),
                                account, transfer.amount)
        return True

    # --- Level 4 -----------------------------------------------------------

    def merge_accounts(self, timestamp: int, account_id_1: str,
                       account_id_2: str) -> bool:
        self._expire(timestamp)
        if account_id_1 == account_id_2:
            return False
        first = self._accounts.get(account_id_1)
        second = self._accounts.get(account_id_2)
        if first is None or second is None:
            return False
        # A pending transfer between the two would become a transfer to itself.
        for transfer in self._transfers.values():
            if transfer.status != "PENDING":
                continue
            ends = {self._resolve(transfer.source), self._resolve(transfer.target)}
            if ends == {first, second}:
                transfer.status = "CANCELED"
                self._resolve(transfer.source).balance += transfer.amount
        first.balance += second.balance
        first.activity += second.activity
        first.history = sorted(first.history + second.history,
                               key=lambda entry: entry.sequence)
        second.merged_into = first
        del self._accounts[account_id_2]
        return True

    def get_history(self, timestamp: int, account_id: str) -> list[str] | None:
        self._expire(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        return [str(entry) for entry in account.history]
