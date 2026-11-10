"""Level 2 — transfers and activity (hidden cases)."""
from icf_testkit import case, expect


@case("refused operations add no activity")
def refused_no_activity(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 5)
    bank.withdraw(4, "a", 50)
    bank.transfer(5, "a", "b", 50)
    expect(bank.top_activity(6, 2), ["a(5)", "b(0)"])


@case("ties are broken by id in string order; n = 0 is empty")
def ties(Bank):
    bank = Bank()
    for i, name in enumerate(("b", "a", "B"), start=1):
        bank.create_account(i, name)
        bank.deposit(10 + i, name, 7)
    expect(bank.top_activity(20, 5), ["B(7)", "a(7)", "b(7)"])
    expect(bank.top_activity(21, 0), [])


@case("an empty bank has no ranking")
def empty(Bank):
    bank = Bank()
    expect(bank.top_activity(1, 3), [])
    bank.create_account(2, "x")
    expect(bank.top_activity(3, 3), ["x(0)"])


@case("both sides of a transfer gain activity")
def both_sides(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 20)
    bank.transfer(4, "a", "b", 20)
    bank.transfer(5, "b", "a", 20)
    expect(bank.top_activity(6, 2), ["a(60)", "b(40)"])
