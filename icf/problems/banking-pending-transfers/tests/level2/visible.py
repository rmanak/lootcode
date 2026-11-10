"""Level 2 — transfers and activity (visible cases)."""
from icf_testkit import case, expect


@case("a transfer moves money and returns the source's balance")
def transfer(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 100)
    expect(bank.transfer(4, "a", "b", 40), 60)
    expect(bank.get_balance(5, "b"), 40)


@case("invalid transfers are refused")
def refused(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 10)
    expect(bank.transfer(4, "a", "a", 5), None)
    expect(bank.transfer(5, "a", "zed", 5), None)
    expect(bank.transfer(6, "a", "b", 11), None)
    expect(bank.get_balance(7, "a"), 10)


@case("activity counts money in and out, ranked with ties by id")
def activity(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
    bank.deposit(4, "a", 100)        # a: 100
    bank.transfer(5, "a", "b", 30)   # a: 130, b: 30
    bank.withdraw(6, "b", 10)        # b: 40
    expect(bank.top_activity(7, 3), ["a(130)", "b(40)", "c(0)"])
    expect(bank.top_activity(8, 1), ["a(130)"])
