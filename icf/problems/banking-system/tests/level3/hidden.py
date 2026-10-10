"""Level 3 — payments and cashback (hidden cases)."""
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



@case("cashback lands even though nothing happens at its due moment")
def cashback_lands_unattended(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 1000)
    bank.pay(3, "alice", 500)
    # Nothing at all is called between ts=3 and this query, far past the due
    # time: the credit is owed at 3 + DAY regardless.
    expect(peek(bank, 3 + 5 * DAY, "alice"), 510, "500 left + 10 cashback")


@case("cashback can be spent once it has arrived")
def cashback_is_spendable(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 1000)
    bank.pay(3, "alice", 1000)                    # cashback 20, due 3 + DAY
    expect(bank.pay(4, "alice", 20), None, "the money is not back yet")
    expect(bank.pay(3 + DAY, "alice", 20), "payment2", "now it is")


@case("a refused payment does not consume a payment id")
def refused_payment_keeps_the_counter(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    expect(bank.pay(3, "alice", 1000), None)
    expect(bank.pay(4, "alice", 50), "payment1", "the first payment is number 1")


@case("the payment counter is shared by the whole bank")
def counter_is_global(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 500)
    bank.deposit(4, "bob", 500)
    expect(bank.pay(5, "alice", 10), "payment1")
    expect(bank.pay(6, "bob", 10), "payment2")
    expect(bank.pay(7, "alice", 10), "payment3")


@case("a payment too small to earn anything still completes")
def tiny_payment(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    payment = bank.pay(3, "alice", 49)            # 0.98 → 0
    expect(bank.get_payment_status(4, "alice", payment), "IN_PROGRESS")
    expect(bank.get_payment_status(3 + DAY, "alice", payment), "CASHBACK_RECEIVED")
    expect(peek(bank, 3 + DAY + 1, "alice"), 51, "nothing came back")


@case("several payments settle independently, each at its own due time")
def payments_settle_independently(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 10_000)
    first = bank.pay(3, "alice", 5_000)           # 100 back at 3 + DAY
    second = bank.pay(100, "alice", 1_000)        # 20 back at 100 + DAY
    expect(bank.get_payment_status(3 + DAY, "alice", first), "CASHBACK_RECEIVED")
    expect(bank.get_payment_status(3 + DAY, "alice", second), "IN_PROGRESS")
    expect(peek(bank, 3 + DAY + 1, "alice"), 4100)
    expect(peek(bank, 100 + DAY, "alice"), 4120)


@case("cashback does not reduce what the account has spent")
def cashback_does_not_offset_spending(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 1000)
    bank.pay(3, "alice", 1000)
    expect(bank.top_spenders(3 + DAY + 1, 1), ["alice(1000)"])
