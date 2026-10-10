"""Level 4 — merging accounts (visible cases)."""
from icf_testkit import case, expect

DAY = 86_400_000


@case("merging adds the second account's balance to the first")
def merge_sums_balances(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 100)
    bank.deposit(4, "bob", 50)
    expect(bank.merge_accounts(5, "alice", "bob"), True)
    expect(bank.get_balance(6, "alice", 6), 150)


@case("the merged-away id is gone")
def merged_id_disappears(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "bob", 50)
    bank.merge_accounts(4, "alice", "bob")
    expect(bank.get_balance(5, "alice", 5), 50, "the money moved to alice")
    expect(bank.deposit(6, "bob", 10), None, "bob no longer exists")
    expect(bank.get_balance(7, "bob", 3), None)


@case("merging is refused for the same id or a missing account")
def merge_invalid(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    expect(bank.merge_accounts(2, "alice", "alice"), False)
    expect(bank.merge_accounts(3, "alice", "ghost"), False)
    expect(bank.merge_accounts(4, "ghost", "alice"), False)
    expect(bank.get_balance(5, "alice", 5), 0, "alice is untouched")


@case("spending totals are merged too")
def merge_sums_spending(Bank):
    bank = Bank()
    for index, name in enumerate(("alice", "bob", "carol"), start=1):
        bank.create_account(index, name)
    bank.deposit(4, "alice", 1000)
    bank.deposit(5, "bob", 1000)
    bank.transfer(6, "alice", "carol", 300)
    bank.transfer(7, "bob", "carol", 400)
    bank.merge_accounts(8, "alice", "bob")
    expect(bank.top_spenders(9, 2), ["alice(700)", "carol(0)"])


@case("get_balance answers as of a moment, and None before the account existed")
def balance_history(Bank):
    bank = Bank()
    bank.create_account(10, "alice")
    bank.deposit(20, "alice", 100)
    bank.deposit(30, "alice", 50)
    expect(bank.get_balance(40, "alice", 5), None, "not created yet")
    expect(bank.get_balance(40, "alice", 10), 0, "created, still empty")
    expect(bank.get_balance(40, "alice", 25), 100, "after the first deposit")
    expect(bank.get_balance(40, "alice", 40), 150)


@case("the absorbing account can look up the payments it inherited")
def inherited_payment_status(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "bob", 1000)
    payment = bank.pay(4, "bob", 500)
    bank.merge_accounts(5, "alice", "bob")
    expect(bank.get_payment_status(6, "alice", payment), "IN_PROGRESS")
    expect(bank.get_payment_status(4 + DAY, "alice", payment), "CASHBACK_RECEIVED")
