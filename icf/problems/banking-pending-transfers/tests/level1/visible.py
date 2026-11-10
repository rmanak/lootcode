"""Level 1 — accounts (visible cases)."""
from icf_testkit import case, expect


@case("an account is created once, starting at 0")
def create(Bank):
    bank = Bank()
    expect(bank.create_account(1, "alice"), True)
    expect(bank.create_account(2, "alice"), False)
    expect(bank.get_balance(3, "alice"), 0)


@case("deposit and withdraw return the new balance")
def deposit_withdraw(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    expect(bank.deposit(2, "alice", 100), 100)
    expect(bank.withdraw(3, "alice", 30), 70)
    expect(bank.get_balance(4, "alice"), 70)


@case("a withdrawal larger than the balance is refused")
def overdraw(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 50)
    expect(bank.withdraw(3, "alice", 51), None)
    expect(bank.withdraw(4, "alice", 50), 0, "the whole balance is fine")


@case("operations on a missing account return None")
def missing(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    expect(bank.deposit(2, "bob", 5), None)
    expect(bank.withdraw(3, "bob", 5), None)
    expect(bank.get_balance(4, "bob"), None)
    expect(bank.deposit(5, "alice", 5), 5)
