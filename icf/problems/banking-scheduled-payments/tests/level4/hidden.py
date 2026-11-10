"""Level 4 — merging accounts and past balances (hidden cases)."""
from icf_testkit import case, expect


@case("a re-created id answers for its new life and its old one")
def recreated_id(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "b", 900)
    bank.merge_accounts(4, "a", "b")
    expect(bank.create_account(6, "b"), True)
    bank.deposit(7, "b", 5)
    expect(bank.get_balance(8, "b", 3), 900, "the old b")
    expect(bank.get_balance(9, "b", 4), None, "between the merge and re-creation")
    expect(bank.get_balance(10, "b", 5), None)
    expect(bank.get_balance(11, "b", 6), 0, "the new b")
    expect(bank.get_balance(12, "b", 7), 5)
    expect(bank.top_spenders(13, 3), ["a(0)", "b(0)"], "the new b inherits no spending")


@case("the new owner of a re-created id cannot see the old payments")
def recreated_id_payments(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    payment = bank.schedule_payment(3, "b", 5, 100)
    bank.merge_accounts(4, "a", "b")
    bank.create_account(5, "b")
    expect(bank.get_payment_status(6, "b", payment), None)
    expect(bank.cancel_payment(7, "b", payment), False)
    expect(bank.cancel_payment(8, "a", payment), True)


@case("a scheduled payment shows in the history at its due time")
def payment_dated_at_due(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 100)
    bank.schedule_payment(3, "a", 30, 7)            # due at 10
    expect(bank.get_balance(50, "a", 9), 100)
    expect(bank.get_balance(51, "a", 10), 70)
    expect(bank.get_balance(52, "a", 49), 70)


@case("merges chain, and payments follow the money to the end")
def chained(Bank):
    bank = Bank()
    for i, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(i, name)
    bank.deposit(4, "a", 100)
    payment = bank.schedule_payment(5, "c", 60, 20)         # due 25
    bank.merge_accounts(6, "b", "c")
    bank.merge_accounts(7, "a", "b")
    expect(bank.get_payment_status(8, "a", payment), "SCHEDULED")
    expect(bank.get_payment_status(9, "b", payment), None)
    expect(bank.get_balance(30, "a", 30), 40)
    expect(bank.top_spenders(31, 3), ["a(60)"])
    expect(bank.get_balance(32, "b", 6), 0, "b existed between 2 and 7")
    expect(bank.get_balance(33, "c", 6), None, "c was merged at 6")


@case("a merge of two accounts with transfers between them keeps totals right")
def merge_after_mutual_transfers(Bank):
    bank = Bank()
    bank.create_account(1, "x")
    bank.create_account(2, "y")
    bank.deposit(3, "x", 100)
    bank.transfer(4, "x", "y", 30)
    bank.transfer(5, "y", "x", 10)
    bank.merge_accounts(6, "y", "x")
    expect(bank.top_spenders(7, 2), ["y(40)"])
    expect(bank.get_balance(8, "y", 7), 100)
    expect(bank.get_balance(9, "x", 5), 80)
    expect(bank.get_balance(10, "y", 5), 20)


@case("a payment skipped after a merge is judged against the merged balance")
def skip_after_merge(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 10)
    bank.deposit(4, "b", 10)
    payment = bank.schedule_payment(5, "a", 25, 10)         # due 15
    bank.merge_accounts(6, "a", "b")
    expect(bank.get_payment_status(15, "a", payment), "SKIPPED", "20 < 25")
    expect(bank.get_balance(16, "a", 15), 20)
