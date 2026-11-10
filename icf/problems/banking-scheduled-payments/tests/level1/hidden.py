"""Level 1 — accounts and transfers (hidden cases)."""
import random

class Peeker:
    """Reads balances before level 4 gives us `get_balance`.

    The only way to observe a balance with levels 1-3 is the value `deposit`
    returns, and amounts are positive — so this nudges the account by 1 and
    subtracts every nudge it has made, leaving the reported balance honest.
    """

    def __init__(self):
        self._nudges = {}

    def __call__(self, bank, timestamp, account_id):
        new_balance = bank.deposit(timestamp, account_id, 1)
        if new_balance is None:
            return None
        self._nudges[account_id] = self._nudges.get(account_id, 0) + 1
        return new_balance - self._nudges[account_id]


from icf_testkit import case, expect


@case("a refused create does not reset the account it clashed with")
def failed_create_is_inert(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 400)
    expect(bank.create_account(3, "alice"), False)
    expect(peek(bank, 4, "alice"), 400, "the balance survived")


@case("accounts are independent of each other")
def accounts_are_independent(Bank):
    peek = Peeker()
    bank = Bank()
    for index, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(index, name)
    bank.deposit(4, "a", 10)
    expect(bank.deposit(5, "b", 5), 5)
    expect(bank.deposit(6, "c", 7), 7)
    expect(peek(bank, 7, "a"), 10)


@case("money survives a chain of transfers")
def chain_of_transfers(Bank):
    peek = Peeker()
    bank = Bank()
    for index, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(index, name)
    bank.deposit(4, "a", 900)
    expect(bank.transfer(5, "a", "b", 500), 400)
    expect(bank.transfer(6, "b", "c", 500), 0)
    expect(bank.transfer(7, "c", "a", 250), 250)
    expect(peek(bank, 8, "a"), 650)


@case("large amounts are handled exactly, with no float rounding")
def large_amounts(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    huge = 10 ** 15 + 7
    expect(bank.deposit(3, "a", huge), huge)
    expect(bank.transfer(4, "a", "b", huge - 1), 1)
    expect(peek(bank, 5, "b"), huge - 1)


@case("a random workload of deposits and transfers matches a reference model")
def fuzz_against_model(Bank):
    balances = {}
    bank = Bank()
    rng = random.Random(31337)
    names = ["a", "b", "c", "d"]
    for ts in range(1, 500):
        who = rng.choice(names)
        roll = rng.random()
        if roll < 0.1:
            created = who not in balances
            expect(bank.create_account(ts, who), created, f"create at ts={ts}")
            if created:
                balances[who] = 0
        elif roll < 0.5:
            amount = rng.randrange(1, 500)
            expected = None if who not in balances else balances[who] + amount
            expect(bank.deposit(ts, who, amount), expected, f"deposit at ts={ts}")
            if who in balances:
                balances[who] = expected
        else:
            other = rng.choice(names)
            amount = rng.randrange(1, 700)
            ok = (who in balances and other in balances and who != other
                  and balances[who] >= amount)
            expected = balances[who] - amount if ok else None
            expect(bank.transfer(ts, who, other, amount), expected,
                   f"transfer {who}->{other} of {amount} at ts={ts}")
            if ok:
                balances[who] -= amount
                balances[other] += amount
