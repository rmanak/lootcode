"""Checkpoint: the reference solution after level 3 only.

The later levels' methods are removed; what remains is enough to pass
levels 1-3 and to fail level 4."""

from bisect import bisect_right
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class BalancePoint:
    """What an account's balance became at `at`."""

    at: int
    balance: int


@dataclass(slots=True, eq=False)     # an account is an identity, not a value
class Account:
    account_id: str
    opened_at: int
    balance: int = 0
    outgoing: int = 0
    history: list[BalancePoint] = field(default_factory=list)
    #: When the account stopped holding its id (merged away), or None.
    closed_at: int | None = None
    #: The account that absorbed this one.
    merged_into: "Account | None" = None

    def __post_init__(self) -> None:
        self.history.append(BalancePoint(self.opened_at, 0))

    def record(self, timestamp: int) -> None:
        """Note the current balance, replacing an entry made at this moment."""
        if self.history[-1].at == timestamp:
            self.history[-1] = BalancePoint(timestamp, self.balance)
        else:
            self.history.append(BalancePoint(timestamp, self.balance))

    def held_id_at(self, time_at: int) -> bool:
        return self.opened_at <= time_at and (self.closed_at is None
                                              or time_at < self.closed_at)

    def balance_at(self, time_at: int) -> int:
        index = bisect_right([point.at for point in self.history], time_at)
        return self.history[index - 1].balance


@dataclass(slots=True)
class Payment:
    payment_id: str
    number: int          # creation order, the tie-break between equal due times
    account: Account     # the account that scheduled it, merged away or not
    amount: int
    due: int
    status: str = "SCHEDULED"


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}
        self._lives: dict[str, list[Account]] = {}
        self._payments: dict[str, Payment] = {}
        self._payment_count = 0

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def _resolve(account: Account) -> Account:
        """Follow merges to the account that now owns this one's money."""
        while account.merged_into is not None:
            account = account.merged_into
        return account

    def _process(self, timestamp: int) -> None:
        """Run every scheduled payment due at or before `timestamp`."""
        due = sorted((p for p in self._payments.values()
                      if p.status == "SCHEDULED" and p.due <= timestamp),
                     key=lambda p: (p.due, p.number))
        for payment in due:
            owner = self._resolve(payment.account)
            if owner.balance < payment.amount:
                payment.status = "SKIPPED"
                continue
            owner.balance -= payment.amount
            owner.outgoing += payment.amount
            owner.record(payment.due)
            payment.status = "EXECUTED"

    def _owned_payment(self, account_id: str, payment_id: str) -> Payment | None:
        account = self._accounts.get(account_id)
        payment = self._payments.get(payment_id)
        if account is None or payment is None:
            return None
        if self._resolve(payment.account) is not account:
            return None
        return payment

    # --- Level 1 -----------------------------------------------------------

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._process(timestamp)
        if account_id in self._accounts:
            return False
        account = Account(account_id, timestamp)
        self._accounts[account_id] = account
        self._lives.setdefault(account_id, []).append(account)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        account.balance += amount
        account.record(timestamp)
        return account.balance

    def transfer(self, timestamp: int, source_id: str, target_id: str,
                 amount: int) -> int | None:
        self._process(timestamp)
        source = self._accounts.get(source_id)
        target = self._accounts.get(target_id)
        if source is None or target is None or source is target:
            return None
        if source.balance < amount:
            return None
        source.balance -= amount
        source.outgoing += amount
        target.balance += amount
        source.record(timestamp)
        target.record(timestamp)
        return source.balance

    # --- Level 2 -----------------------------------------------------------

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        self._process(timestamp)
        ranked = sorted(self._accounts.values(),
                        key=lambda account: (-account.outgoing, account.account_id))
        return [f"{account.account_id}({account.outgoing})"
                for account in ranked[:n]]

    # --- Level 3 -----------------------------------------------------------

    def schedule_payment(self, timestamp: int, account_id: str, amount: int,
                         delay: int) -> str | None:
        self._process(timestamp)
        account = self._accounts.get(account_id)
        if account is None:
            return None
        self._payment_count += 1
        payment_id = f"payment{self._payment_count}"
        self._payments[payment_id] = Payment(payment_id, self._payment_count,
                                             account, amount, timestamp + delay)
        return payment_id

    def cancel_payment(self, timestamp: int, account_id: str,
                       payment_id: str) -> bool:
        self._process(timestamp)
        payment = self._owned_payment(account_id, payment_id)
        if payment is None or payment.status != "SCHEDULED":
            return False
        payment.status = "CANCELED"
        return True

    def get_payment_status(self, timestamp: int, account_id: str,
                           payment_id: str) -> str | None:
        self._process(timestamp)
        payment = self._owned_payment(account_id, payment_id)
        return None if payment is None else payment.status

    # --- Level 4 -----------------------------------------------------------

