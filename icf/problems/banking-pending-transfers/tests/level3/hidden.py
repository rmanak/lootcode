"""Level 3 — pending transfers (hidden cases)."""
from icf_testkit import case, expect

DAY = 86_400_000


@case("held money cannot be spent twice")
def no_double_spend(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 100)
    bank.initiate_transfer(4, "a", "b", 80)
    expect(bank.withdraw(5, "a", 30), None)
    expect(bank.transfer(6, "a", "b", 30), None)
    expect(bank.initiate_transfer(7, "a", "b", 30), None)
    expect(bank.withdraw(8, "a", 20), 0)


@case("activity counts a pending transfer only once accepted")
def activity_on_accept(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 100)
    t1 = bank.initiate_transfer(4, "a", "b", 40)
    bank.initiate_transfer(5, "a", "b", 10)
    expect(bank.top_activity(6, 2), ["a(100)", "b(0)"])
    bank.accept_transfer(7, "b", t1)
    expect(bank.top_activity(8, 2), ["a(140)", "b(40)"])
    expect(bank.top_activity(5 + DAY, 2), ["a(140)", "b(40)"], "the expired one never counts")
    expect(bank.get_balance(5 + DAY + 1, "a"), 60)


@case("accepting one millisecond before expiry works")
def accept_just_in_time(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 5)
    t = bank.initiate_transfer(4, "a", "b", 5)
    expect(bank.accept_transfer(4 + DAY - 1, "b", t), True)
    expect(bank.get_balance(4 + DAY + 5, "a"), 0, "nothing is refunded")
    expect(bank.get_balance(4 + DAY + 6, "b"), 5)


@case("an expired hold is back in time for the operation at that moment")
def refund_before_operation(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 20)
    bank.initiate_transfer(4, "a", "b", 20)
    expect(bank.withdraw(4 + DAY, "a", 20), 0)


@case("transfer ids count up across the bank, and expired ids stay used")
def ids(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
        bank.deposit(10 + i, name, 100)
    expect(bank.initiate_transfer(20, "a", "b", 1), "transfer1")
    expect(bank.initiate_transfer(21, "c", "a", 1), "transfer2")
    expect(bank.initiate_transfer(21 + DAY, "b", "c", 1), "transfer3")


@case("a transfer can be accepted while the source has spent the rest")
def source_spent(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 10)
    t = bank.initiate_transfer(4, "a", "b", 6)
    bank.withdraw(5, "a", 4)
    expect(bank.accept_transfer(6, "b", t), True)
    expect(bank.get_balance(7, "b"), 6)
