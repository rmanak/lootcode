"""Level 3 — payments and cashback (visible cases)."""
from icf_testkit import case, expect

DAY = 86_400_000

class Peeker:
    """Reads balances before level 4 gives us `get_balance`.

    The only way to observe a balance with levels 1-3 is the value `deposit`
    returns, and amounts are positive — so this nudges the account by 1 and
    subtracts every nudge it has made, leaving the reported balance honest.
    """

    def __init__(self):
        self._nudges = {}

    def __call__(self, bank, timestamp, account_id):
        new_balance = bank.deposit(timestamp, account_id, 1)
        if new_balance is None:
            return None
        self._nudges[account_id] = self._nudges.get(account_id, 0) + 1
        return new_balance - self._nudges[account_id]



@case("pay withdraws the money and returns a payment id")
def pay_returns_an_id(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 1000)
    expect(bank.pay(3, "alice", 400), "payment1")
    expect(bank.pay(4, "alice", 100), "payment2", "ids count up across the bank")
    expect(peek(bank, 5, "alice"), 500, "1000 - 400 - 100")


@case("a payment that cannot be funded is refused")
def pay_insufficient(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    expect(bank.pay(3, "alice", 101), None, "not enough funds")
    expect(bank.pay(4, "ghost", 10), None, "no such account")
    expect(peek(bank, 5, "alice"), 100, "nothing was withdrawn")


@case("a payment is in progress until its cashback lands, 24 hours later")
def cashback_timing(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 2000)
    payment = bank.pay(3, "alice", 1000)
    expect(bank.get_payment_status(4, "alice", payment), "IN_PROGRESS")
    expect(bank.get_payment_status(3 + DAY - 1, "alice", payment), "IN_PROGRESS",
           "one millisecond short of a day")
    expect(bank.get_payment_status(3 + DAY, "alice", payment), "CASHBACK_RECEIVED")


@case("cashback is two percent, rounded down")
def cashback_is_floored(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 5000)
    bank.pay(3, "alice", 1049)              # 20.98 → 20
    expect(peek(bank, 4, "alice"), 3951)
    expect(peek(bank, 3 + DAY, "alice"), 3971, "3951 + 20")


@case("a payment belongs to the account that made it")
def payment_ownership(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 500)
    payment = bank.pay(4, "alice", 100)
    expect(bank.get_payment_status(5, "alice", payment), "IN_PROGRESS",
           "the account that made it")
    expect(bank.get_payment_status(5, "bob", payment), None, "not bob's payment")
    expect(bank.get_payment_status(6, "alice", "payment9"), None, "no such payment")
    expect(bank.get_payment_status(7, "ghost", payment), None, "no such account")


@case("paying counts towards what the account has spent")
def payments_count_as_spending(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 1000)
    bank.deposit(4, "bob", 1000)
    bank.transfer(5, "bob", "alice", 100)
    bank.pay(6, "alice", 500)
    expect(bank.top_spenders(7, 2), ["alice(500)", "bob(100)"])
