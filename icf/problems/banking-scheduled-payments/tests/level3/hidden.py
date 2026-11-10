"""Level 3 — scheduled payments (hidden cases)."""
import random

from icf_testkit import case, expect


@case("payments due at the same moment run in the order they were scheduled")
def ties_by_creation(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 100)
    late = bank.schedule_payment(3, "a", 80, 20)    # due at 23, scheduled first
    early = bank.schedule_payment(4, "a", 60, 19)   # due at 23, scheduled second
    expect(bank.get_payment_status(23, "a", late), "EXECUTED")
    expect(bank.get_payment_status(24, "a", early), "SKIPPED",
           "only 20 was left when the second one ran")


@case("an earlier due time runs first even if it was scheduled later")
def earlier_due_first(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 100)
    slow = bank.schedule_payment(3, "a", 80, 50)    # due at 53
    fast = bank.schedule_payment(4, "a", 60, 10)    # due at 14
    bank.deposit(100, "a", 1)
    expect(bank.get_payment_status(101, "a", fast), "EXECUTED")
    expect(bank.get_payment_status(102, "a", slow), "SKIPPED")


@case("a payment can empty the account exactly")
def exact_balance(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 75)
    payment = bank.schedule_payment(3, "a", 75, 1)
    expect(bank.get_payment_status(4, "a", payment), "EXECUTED")
    expect(bank.deposit(5, "a", 5), 5)


@case("a transfer at the due timestamp sees the balance after the payment")
def due_before_transfer(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "a", 100)
    bank.schedule_payment(4, "a", 60, 6)            # due at 10
    expect(bank.transfer(10, "a", "b", 50), None, "only 40 left")
    expect(bank.transfer(11, "a", "b", 40), 0)


@case("money deposited before the due time makes the payment affordable")
def deposit_rescues(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    payment = bank.schedule_payment(2, "a", 30, 10)
    bank.deposit(5, "a", 30)
    expect(bank.get_payment_status(12, "a", payment), "EXECUTED")


@case("cancelling twice, or cancelling a finished payment, fails")
def cancel_finished(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 10)
    p1 = bank.schedule_payment(3, "a", 5, 2)        # due 5, executes
    p2 = bank.schedule_payment(4, "a", 50, 2)       # due 6, skipped
    p3 = bank.schedule_payment(7, "a", 1, 100)
    expect(bank.cancel_payment(8, "a", p1), False, "already executed")
    expect(bank.cancel_payment(9, "a", p2), False, "already skipped")
    expect(bank.cancel_payment(10, "a", p3), True)
    expect(bank.cancel_payment(11, "a", p3), False, "already cancelled")
    expect(bank.get_payment_status(12, "a", p3), "CANCELED")


@case("a skipped or cancelled payment adds nothing to outgoing")
def failed_payments_do_not_count(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 10)
    bank.schedule_payment(3, "a", 50, 2)
    p = bank.schedule_payment(4, "a", 5, 10)
    bank.cancel_payment(5, "a", p)
    expect(bank.top_spenders(100, 1), ["a(0)"])


def model_run(seed):
    rng = random.Random(seed)
    names = ["a", "b", "c"]
    balances = {n: 0 for n in names}
    outgoing = {n: 0 for n in names}
    pending = []          # [due, number, owner, amount, status]
    statuses = {}
    calls = []

    def settle(ts):
        for p in sorted((p for p in pending if p[4] == "S" and p[0] <= ts),
                        key=lambda p: (p[0], p[1])):
            if balances[p[2]] >= p[3]:
                balances[p[2]] -= p[3]
                outgoing[p[2]] += p[3]
                p[4] = "EXECUTED"
            else:
                p[4] = "SKIPPED"

    ts = 10
    count = 0
    for _ in range(120):
        ts += rng.randint(1, 4)
        settle(ts)
        kind = rng.random()
        who = rng.choice(names)
        if kind < 0.3:
            amount = rng.randint(1, 40)
            balances[who] += amount
            calls.append(("deposit", ts, who, amount, balances[who]))
        elif kind < 0.6:
            amount, delay = rng.randint(1, 60), rng.randint(1, 15)
            count += 1
            pending.append([ts + delay, count, who, amount, "S"])
            calls.append(("schedule", ts, who, amount, delay, f"payment{count}"))
        elif kind < 0.75 and pending:
            p = rng.choice(pending)
            ok = p[4] == "S" and p[2] == who
            if ok:
                p[4] = "CANCELED"
            calls.append(("cancel", ts, who, f"payment{p[1]}", ok))
        else:
            calls.append(("top", ts, [f"{n}({outgoing[n]})" for n in
                                      sorted(names, key=lambda n: (-outgoing[n], n))]))
    return calls


@case("a long random run matches a reference model")
def random_against_model(Bank):
    for seed in (1, 2, 3):
        bank = Bank()
        for i, name in enumerate(("a", "b", "c"), start=1):
            bank.create_account(i, name)
        for call in model_run(seed):
            if call[0] == "deposit":
                expect(bank.deposit(call[1], call[2], call[3]), call[4])
            elif call[0] == "schedule":
                expect(bank.schedule_payment(call[1], call[2], call[3], call[4]), call[5])
            elif call[0] == "cancel":
                expect(bank.cancel_payment(call[1], call[2], call[3]), call[4],
                       f"cancel {call[3]} by {call[2]} at {call[1]}")
            else:
                expect(bank.top_spenders(call[1], 3), call[2], f"at {call[1]}")
