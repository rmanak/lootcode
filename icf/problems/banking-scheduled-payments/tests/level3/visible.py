"""Level 3 — scheduled payments (visible cases)."""
from icf_testkit import case, expect


@case("payment ids count up across the whole bank")
def ids_count_up(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    expect(bank.schedule_payment(3, "alice", 10, 100), "payment1")
    expect(bank.schedule_payment(4, "bob", 10, 100), "payment2")
    expect(bank.schedule_payment(5, "alice", 10, 100), "payment3")


@case("a payment runs at timestamp + delay, not before")
def runs_when_due(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    payment = bank.schedule_payment(3, "alice", 30, 10)     # due at 13
    expect(bank.get_payment_status(12, "alice", payment), "SCHEDULED")
    expect(bank.deposit(12, "alice", 1), 101,
           "nothing withdrawn yet at 12")
    expect(bank.get_payment_status(13, "alice", payment), "EXECUTED")
    expect(bank.deposit(14, "alice", 1), 72, "102 - 30 = 72")


@case("a due payment runs even if no operation is called at its due time")
def runs_without_a_call_at_due(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    bank.schedule_payment(3, "alice", 40, 5)                # due at 8
    expect(bank.deposit(1000, "alice", 1), 61)


@case("a payment the account cannot afford when due is skipped")
def skipped_when_short(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 50)
    payment = bank.schedule_payment(3, "alice", 80, 10)
    expect(payment, "payment1", "scheduling does not check the balance")
    expect(bank.get_payment_status(13, "alice", payment), "SKIPPED")
    expect(bank.deposit(14, "alice", 100), 150, "a skipped payment withdraws nothing")
    expect(bank.get_payment_status(15, "alice", payment), "SKIPPED",
           "it is never retried")


@case("cancel works before the due time and fails at it")
def cancel_before_due(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    first = bank.schedule_payment(3, "alice", 10, 10)       # due at 13
    second = bank.schedule_payment(4, "alice", 10, 10)      # due at 14
    expect(bank.cancel_payment(5, "alice", first), True)
    expect(bank.get_payment_status(6, "alice", first), "CANCELED")
    expect(bank.cancel_payment(14, "alice", second), False,
           "due payments run before the cancel at the same timestamp")
    expect(bank.deposit(15, "alice", 1), 91, "only the second payment ran")


@case("executed scheduled payments count as outgoing money")
def executed_counts_as_spending(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 100)
    bank.schedule_payment(4, "alice", 70, 10)
    expect(bank.top_spenders(5, 2), ["alice(0)", "bob(0)"], "not executed yet")
    expect(bank.top_spenders(14, 2), ["alice(70)", "bob(0)"])


@case("unknown accounts and foreign payments are refused")
def unknown_and_foreign(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    expect(bank.schedule_payment(3, "zed", 10, 10), None)
    payment = bank.schedule_payment(4, "alice", 10, 10)
    expect(payment, "payment1", "the refused call used up no id")
    expect(bank.get_payment_status(5, "bob", payment), None)
    expect(bank.cancel_payment(6, "bob", payment), False)
    expect(bank.get_payment_status(7, "alice", "payment9"), None)
    expect(bank.get_payment_status(8, "alice", payment), "SCHEDULED")
