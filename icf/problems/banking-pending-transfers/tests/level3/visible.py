"""Level 3 — pending transfers (visible cases)."""
from icf_testkit import case, expect

DAY = 86_400_000


@case("initiating holds the money; accepting delivers it")
def hold_and_accept(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 100)
    expect(bank.initiate_transfer(4, "a", "b", 30), "transfer1")
    expect(bank.get_balance(5, "a"), 70, "the 30 is held")
    expect(bank.get_balance(6, "b"), 0, "not delivered yet")
    expect(bank.accept_transfer(7, "b", "transfer1"), True)
    expect(bank.get_balance(8, "b"), 30)
    expect(bank.accept_transfer(9, "b", "transfer1"), False, "already accepted")


@case("only the recipient can accept")
def recipient_only(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
    bank.deposit(4, "a", 10)
    t = bank.initiate_transfer(5, "a", "b", 10)
    expect(bank.accept_transfer(6, "c", t), False)
    expect(bank.accept_transfer(7, "a", t), False)
    expect(bank.accept_transfer(8, "b", "transfer9"), False)
    expect(bank.accept_transfer(9, "b", t), True)


@case("an unaccepted transfer expires after 24 hours and the money returns")
def expiry(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 50)
    t = bank.initiate_transfer(4, "a", "b", 50)
    expect(bank.get_balance(4 + DAY - 1, "a"), 0)
    expect(bank.accept_transfer(4 + DAY, "b", t), False, "expired at exactly 24h")
    expect(bank.get_balance(4 + DAY + 1, "a"), 50)


@case("initiate is refused like a transfer")
def refused(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 10)
    expect(bank.initiate_transfer(4, "a", "a", 1), None)
    expect(bank.initiate_transfer(5, "a", "zed", 1), None)
    expect(bank.initiate_transfer(6, "a", "b", 11), None)
    expect(bank.initiate_transfer(7, "a", "b", 10), "transfer1", "no id was used up")
