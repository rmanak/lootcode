"""Checkpoint: the reference solution after levels 1-3 (no merging yet).

Two ideas carry the whole thing:

* **An account is an object, and the id is only a lookup.** ``_accounts`` maps
  the id to the account that holds it *now*. A merged-away account keeps its
  own object (its payments still resolve through it), and re-creating the id
  makes a new object with an empty history — so the "merge, then re-create the
  same id" case needs no special handling at all.
* **Cashback is a scheduled balance change.** Every operation first settles
  everything due at or before its timestamp, recording each credit in the
  account's history *at its own due time*, so `get_balance` sees it where it
  belongs even though no call happened at that moment.
"""

from bisect import bisect_right
from dataclasses import dataclass, field

DAY_MS = 86_400_000
CASHBACK_RATE = 0.02


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
    #: Balances in increasing timestamp order, starting at creation — which is
    #: what makes "did not exist yet" answerable.
    history: list[BalancePoint] = field(default_factory=list)
    #: Set when this account is merged away; its money lives in the other one.
    merged_into: "Account | None" = None

    def __post_init__(self) -> None:
        self.history.append(BalancePoint(self.opened_at, 0))

    def record(self, timestamp: int) -> None:
        """Note the current balance, replacing an entry made at this moment."""
        if self.history and self.history[-1].at == timestamp:
            self.history[-1] = BalancePoint(timestamp, self.balance)
        else:
            self.history.append(BalancePoint(timestamp, self.balance))

    def balance_at(self, time_at: int) -> int | None:
        """The balance as of `time_at`, or None if the account did not exist."""
        index = bisect_right([point.at for point in self.history], time_at)
        if index == 0:
            return None
        return self.history[index - 1].balance


@dataclass(frozen=True, slots=True)
class Payment:
    """A payment, remembered so its status can be asked for later."""

    account: Account     # the account it was made from, merged away or not
    due: int             # when its cashback lands


@dataclass(frozen=True, slots=True)
class Cashback:
    """A credit waiting to be paid. `sequence` orders credits due at once."""

    due: int
    sequence: int
    account: Account
    amount: int


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}
        self._payments: dict[str, Payment] = {}
        self._pending: list[Cashback] = []     # kept in due order
        self._payment_count = 0

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def _resolve(account: Account) -> Account:
        """Follow merges to the account that now owns this one's money."""
        while account.merged_into is not None:
            account = account.merged_into
        return account

    def _settle(self, timestamp: int) -> None:
        """Apply every cashback due at or before `timestamp`, in due order."""
        while self._pending and self._pending[0].due <= timestamp:
            cashback = self._pending.pop(0)
            target = self._resolve(cashback.account)
            target.balance += cashback.amount
            target.record(cashback.due)

    def _live(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)

    # --- Level 1 -----------------------------------------------------------

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._settle(timestamp)
        if account_id in self._accounts:
            return False
        self._accounts[account_id] = Account(account_id, timestamp)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._settle(timestamp)
        account = self._live(account_id)
        if account is None:
            return None
        account.balance += amount
        account.record(timestamp)
        return account.balance

    def transfer(self, timestamp: int, source_id: str, target_id: str,
                 amount: int) -> int | None:
        self._settle(timestamp)
        source = self._live(source_id)
        target = self._live(target_id)
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
        self._settle(timestamp)
        ranked = sorted(self._accounts.values(),
                        key=lambda account: (-account.outgoing, account.account_id))
        return [f"{account.account_id}({account.outgoing})"
                for account in ranked[:n]]

    # --- Level 3 -----------------------------------------------------------

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        self._settle(timestamp)
        account = self._live(account_id)
        if account is None or account.balance < amount:
            return None
        account.balance -= amount
        account.outgoing += amount
        account.record(timestamp)

        self._payment_count += 1
        payment_id = f"payment{self._payment_count}"
        due = timestamp + DAY_MS
        self._payments[payment_id] = Payment(account, due)
        self._pending.append(Cashback(due, self._payment_count, account,
                                      int(amount * CASHBACK_RATE)))
        self._pending.sort(key=lambda cashback: (cashback.due, cashback.sequence))
        return payment_id

    def get_payment_status(self, timestamp: int, account_id: str,
                           payment: str) -> str | None:
        self._settle(timestamp)
        account = self._live(account_id)
        record = self._payments.get(payment)
        if account is None or record is None:
            return None
        if self._resolve(record.account) is not account:
            return None
        return "CASHBACK_RECEIVED" if record.due <= timestamp else "IN_PROGRESS"
