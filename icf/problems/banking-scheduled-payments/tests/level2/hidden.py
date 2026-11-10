"""Level 2 — who spends the most (hidden cases)."""
import random

from icf_testkit import case, expect


@case("deposits and incoming transfers never count as spending")
def only_outgoing_counts(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 5000)
    bank.transfer(4, "alice", "bob", 4000)
    expect(bank.top_spenders(5, 2), ["alice(4000)", "bob(0)"],
           "bob received 4000 but has sent nothing")


@case("a refused transfer adds nothing to the total")
def refused_transfers_do_not_count(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 100)
    bank.transfer(4, "alice", "bob", 5000)      # insufficient
    bank.transfer(5, "alice", "ghost", 10)      # no such account
    bank.transfer(6, "alice", "alice", 10)      # same account
    expect(bank.top_spenders(7, 2), ["alice(0)", "bob(0)"])


@case("the ranking keeps up as totals change")
def ranking_is_current(Bank):
    bank = Bank()
    for index, name in enumerate(("a", "b"), start=1):
        bank.create_account(index, name)
    bank.deposit(3, "a", 1000)
    bank.deposit(4, "b", 1000)
    bank.transfer(5, "a", "b", 100)
    expect(bank.top_spenders(6, 1), ["a(100)"])
    bank.transfer(7, "b", "a", 900)
    expect(bank.top_spenders(8, 1), ["b(900)"])
    expect(bank.top_spenders(9, 2), ["b(900)", "a(100)"])


@case("ids are compared as strings, so '10' sorts before '9'")
def id_order_is_lexicographic(Bank):
    bank = Bank()
    for index, name in enumerate(("9", "10", "1"), start=1):
        bank.create_account(index, name)
    expect(bank.top_spenders(4, 3), ["1(0)", "10(0)", "9(0)"])


@case("the ranking matches a reference model over a random workload")
def fuzz_ranking(Bank):
    outgoing = {}
    balances = {}
    bank = Bank()
    rng = random.Random(777)
    names = ["ann", "bo", "cy", "dee", "ed"]
    for index, name in enumerate(names, start=1):
        bank.create_account(index, name)
        bank.deposit(index + 10, name, 10_000)
        outgoing[name] = 0
        balances[name] = 10_000

    ts = 100
    for _ in range(200):
        ts += 1
        source, target = rng.sample(names, 2)
        amount = rng.randrange(1, 900)
        if balances[source] >= amount:
            bank.transfer(ts, source, target, amount)
            balances[source] -= amount
            balances[target] += amount
            outgoing[source] += amount
        if ts % 7 == 0:
            n = rng.randrange(1, 6)
            wanted = [f"{name}({total})" for name, total in
                      sorted(outgoing.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]
            expect(bank.top_spenders(ts, n), wanted, f"top_spenders({n}) at ts={ts}")
