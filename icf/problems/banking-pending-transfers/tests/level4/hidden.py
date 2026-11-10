"""Level 4 — merging accounts and history (hidden cases)."""
from icf_testkit import case, expect

DAY = 86_400_000


@case("a re-created id does not inherit the merged-away history")
def recreated(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "b", 9)
    bank.merge_accounts(4, "a", "b")
    expect(bank.create_account(5, "b"), True)
    expect(bank.get_history(6, "b"), [])
    expect(bank.get_balance(7, "b"), 0)
    expect(bank.top_activity(8, 5), ["a(9)", "b(0)"])


@case("transfers addressed to the merged account are accepted by the absorber")
def incoming_pending(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
    bank.deposit(4, "c", 30)
    t = bank.initiate_transfer(5, "c", "b", 30)
    bank.merge_accounts(6, "a", "b")
    expect(bank.accept_transfer(7, "a", t), True)
    expect(bank.get_balance(8, "a"), 30)


@case("a re-created id cannot accept what was sent to the old one")
def recreated_cannot_accept(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
    bank.deposit(4, "c", 30)
    t = bank.initiate_transfer(5, "c", "b", 30)
    bank.merge_accounts(6, "a", "b")
    bank.create_account(7, "b")
    expect(bank.accept_transfer(8, "b", t), False)
    expect(bank.accept_transfer(9, "a", t), True)


@case("an outgoing hold of the merged account refunds to the absorber")
def outgoing_refund(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
    bank.deposit(4, "b", 25)
    bank.initiate_transfer(5, "b", "c", 25)
    bank.merge_accounts(6, "a", "b")
    expect(bank.get_balance(7, "a"), 0, "the 25 is still held")
    expect(bank.get_balance(5 + DAY, "a"), 25)


@case("a pending transfer between the two merged accounts is cancelled")
def internal_cancelled(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 60)
    t = bank.initiate_transfer(4, "a", "b", 60)
    bank.merge_accounts(5, "a", "b")
    expect(bank.get_balance(6, "a"), 60, "the hold came back")
    expect(bank.accept_transfer(7, "a", t), False)
    expect(bank.get_history(8, "a"), ["3:deposit:60"])
    expect(bank.get_balance(4 + DAY, "a"), 60, "and is not refunded twice")


@case("merged histories interleave by time, and a transfer between them keeps both sides")
def interleave(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 10)
    bank.deposit(4, "b", 20)
    bank.transfer(5, "b", "a", 5)
    bank.withdraw(6, "a", 1)
    bank.merge_accounts(7, "b", "a")
    expect(bank.get_history(8, "b"),
           ["3:deposit:10", "4:deposit:20", "5:transfer_out:5",
            "5:transfer_in:5", "6:withdraw:1"])
    expect(bank.top_activity(9, 1), ["b(41)"])


@case("merges chain, and the end account holds everything")
def chained(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c", "d"), start=1):
        bank.create_account(i, name)
    bank.deposit(5, "c", 7)
    t = bank.initiate_transfer(6, "c", "d", 7)
    bank.merge_accounts(7, "b", "c")
    bank.merge_accounts(8, "a", "b")
    bank.accept_transfer(9, "d", t)
    expect(bank.get_history(10, "a"), ["5:deposit:7", "9:transfer_out:7"])
    expect(bank.get_history(11, "d"), ["9:transfer_in:7"])
