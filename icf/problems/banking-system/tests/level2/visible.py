"""Level 2 — who spends the most (visible cases)."""
from icf_testkit import case, expect


def fund(bank, names, amount=1000):
    """Open every named account and give each the same starting balance."""
    ts = 0
    for name in names:
        ts += 1
        bank.create_account(ts, name)
    for name in names:
        ts += 1
        bank.deposit(ts, name, amount)
    return ts


@case("accounts are ranked by what has left them, highest first")
def ranked_by_outgoing(Bank):
    bank = Bank()
    ts = fund(bank, ("alice", "bob", "carol"))
    bank.transfer(ts + 1, "alice", "bob", 300)
    bank.transfer(ts + 2, "carol", "alice", 500)
    expect(bank.top_spenders(ts + 3, 3),
           ["carol(500)", "alice(300)", "bob(0)"])


@case("accounts that have sent the same amount are ordered by id")
def ties_break_on_id(Bank):
    bank = Bank()
    ts = fund(bank, ("bob", "alice"))
    bank.transfer(ts + 1, "bob", "alice", 300)
    bank.transfer(ts + 2, "alice", "bob", 300)
    expect(bank.top_spenders(ts + 3, 2), ["alice(300)", "bob(300)"])


@case("asking for more accounts than exist returns all of them")
def n_larger_than_the_bank(Bank):
    bank = Bank()
    ts = fund(bank, ("alice", "bob"))
    bank.transfer(ts + 1, "alice", "bob", 10)
    expect(bank.top_spenders(ts + 2, 99), ["alice(10)", "bob(0)"])


@case("an account that has never sent anything still appears, with zero")
def zero_spenders_appear(Bank):
    bank = Bank()
    ts = fund(bank, ("alice", "bob"))
    expect(bank.top_spenders(ts + 1, 2), ["alice(0)", "bob(0)"])


@case("asking for none returns none, and an empty bank ranks nothing")
def degenerate_requests(Bank):
    bank = Bank()
    expect(bank.top_spenders(1, 5), [])
    bank.create_account(2, "alice")
    expect(bank.top_spenders(3, 0), [])
