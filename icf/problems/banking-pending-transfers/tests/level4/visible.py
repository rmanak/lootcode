"""Level 4 — merging accounts and history (visible cases)."""
from icf_testkit import case, expect


@case("history lists completed transactions in order")
def history(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 100)
    bank.withdraw(4, "a", 10)
    bank.transfer(5, "a", "b", 20)
    expect(bank.get_history(6, "a"),
           ["3:deposit:100", "4:withdraw:10", "5:transfer_out:20"])
    expect(bank.get_history(7, "b"), ["5:transfer_in:20"])
    expect(bank.get_history(8, "zed"), None)


@case("a pending transfer enters history when it is accepted")
def pending_history(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 50)
    t = bank.initiate_transfer(4, "a", "b", 50)
    expect(bank.get_history(5, "a"), ["3:deposit:50"])
    bank.accept_transfer(6, "b", t)
    expect(bank.get_history(7, "a"), ["3:deposit:50", "6:transfer_out:50"])


@case("a merge combines balances, activity and history")
def merge(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "b", 40)
    bank.deposit(4, "a", 10)
    expect(bank.merge_accounts(5, "a", "b"), True)
    expect(bank.get_balance(6, "a"), 50)
    expect(bank.get_balance(7, "b"), None)
    expect(bank.top_activity(8, 5), ["a(50)"])
    expect(bank.get_history(9, "a"), ["3:deposit:40", "4:deposit:10"])


@case("invalid merges are refused")
def merge_refused(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    expect(bank.merge_accounts(2, "a", "a"), False)
    expect(bank.merge_accounts(3, "a", "zed"), False)
    expect(bank.merge_accounts(4, "zed", "a"), False)
    expect(bank.get_balance(5, "a"), 0)
