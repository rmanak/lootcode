"""Level 1 — accounts (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a refused create leaves the account as it was")
def refused_create(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 9)
    bank.create_account(3, "a")
    expect(bank.get_balance(4, "a"), 9)


@case("a refused withdrawal changes nothing")
def refused_withdraw(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.deposit(2, "a", 10)
    bank.withdraw(3, "a", 11)
    expect(bank.get_balance(4, "a"), 10)


@case("ids are case-sensitive")
def ids(Bank):
    bank = Bank()
    bank.create_account(1, "A")
    expect(bank.create_account(2, "a"), True)
    bank.deposit(3, "A", 4)
    expect(bank.get_balance(4, "a"), 0)


@case("a random run matches a reference")
def random_model(Bank):
    rng = random.Random(1)
    bank = Bank()
    model = {}
    for ts in range(1, 500):
        who = rng.choice("abcd")
        op = rng.random()
        if op < 0.15:
            expect(bank.create_account(ts, who), who not in model)
            model.setdefault(who, 0)
        elif op < 0.5:
            amount = rng.randint(1, 50)
            want = None if who not in model else model[who] + amount
            expect(bank.deposit(ts, who, amount), want)
            if want is not None:
                model[who] = want
        elif op < 0.8:
            amount = rng.randint(1, 50)
            ok = who in model and model[who] >= amount
            expect(bank.withdraw(ts, who, amount), model[who] - amount if ok else None)
            if ok:
                model[who] -= amount
        else:
            expect(bank.get_balance(ts, who), model.get(who))
