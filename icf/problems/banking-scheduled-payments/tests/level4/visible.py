"""Level 4 — merging accounts and past balances (visible cases)."""
from icf_testkit import case, expect


@case("a merge adds the second account's balance to the first")
def merge_adds_balance(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 100)
    bank.deposit(4, "bob", 50)
    expect(bank.merge_accounts(5, "alice", "bob"), True)
    expect(bank.deposit(6, "alice", 1), 151)
    expect(bank.deposit(7, "bob", 1), None, "bob no longer exists")


@case("invalid merges are refused and change nothing")
def merge_refused(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 10)
    expect(bank.merge_accounts(3, "alice", "alice"), False)
    expect(bank.merge_accounts(4, "alice", "zed"), False)
    expect(bank.merge_accounts(5, "zed", "alice"), False)
    expect(bank.deposit(6, "alice", 1), 11)


@case("the absorbing account inherits outgoing totals")
def merge_outgoing(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
    bank.deposit(4, "b", 100)
    bank.transfer(5, "b", "c", 60)
    bank.merge_accounts(6, "a", "b")
    expect(bank.top_spenders(7, 3), ["a(60)", "c(0)"])


@case("a pending payment of the merged account runs from the absorbing one")
def payment_follows_merge(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 100)
    payment = bank.schedule_payment(4, "bob", 70, 10)       # due at 14
    bank.merge_accounts(5, "alice", "bob")
    expect(bank.get_payment_status(6, "alice", payment), "SCHEDULED")
    expect(bank.get_payment_status(14, "alice", payment), "EXECUTED",
           "bob had nothing, but alice's money now pays")
    expect(bank.deposit(15, "alice", 1), 31)


@case("get_balance looks back in time")
def balance_history(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(3, "alice", 100)
    bank.deposit(5, "alice", 20)
    expect(bank.get_balance(6, "alice", 0), None, "not created yet")
    expect(bank.get_balance(7, "alice", 1), 0)
    expect(bank.get_balance(8, "alice", 4), 100)
    expect(bank.get_balance(9, "alice", 5), 120, "the operation at time_at counts")


@case("a merged-away account's past is still queryable, until the merge")
def merged_away_past(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "bob", 40)
    bank.merge_accounts(5, "alice", "bob")
    expect(bank.get_balance(6, "bob", 4), 40)
    expect(bank.get_balance(7, "bob", 5), None, "from the merge on, bob is gone")
    expect(bank.get_balance(8, "alice", 4), 0, "alice before the merge")
    expect(bank.get_balance(9, "alice", 5), 40)
