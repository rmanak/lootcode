"""Level 1 — accounts and transfers (visible cases)."""
from icf_testkit import case, expect

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



@case("an account is created once, and the second attempt is refused")
def create_is_idempotent_by_refusal(Bank):
    bank = Bank()
    expect(bank.create_account(1, "alice"), True)
    expect(bank.create_account(2, "alice"), False, "the id is taken")


@case("deposit returns the new balance")
def deposit_returns_balance(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    expect(bank.deposit(2, "alice", 500), 500)
    expect(bank.deposit(3, "alice", 250), 750, "deposits accumulate")


@case("deposit into an account that does not exist returns None")
def deposit_missing_account(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    expect(bank.deposit(2, "alice", 100), 100, "the account that does exist")
    expect(bank.deposit(3, "ghost", 100), None)


@case("transfer moves the money and returns the source's new balance")
def transfer_moves_money(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 500)
    expect(bank.transfer(4, "alice", "bob", 200), 300)
    expect(peek(bank, 5, "bob"), 200, "bob received 200")


@case("a transfer with insufficient funds is refused and changes nothing")
def transfer_insufficient(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 100)
    expect(bank.transfer(4, "alice", "bob", 101), None)
    expect(peek(bank, 5, "alice"), 100, "alice still has her money")
    expect(peek(bank, 6, "bob"), 0, "bob received nothing")


@case("a transfer to a missing account, or to itself, is refused")
def transfer_invalid_targets(Bank):
    peek = Peeker()
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    expect(bank.transfer(3, "alice", "ghost", 10), None, "no such target")
    expect(bank.transfer(4, "ghost", "alice", 10), None, "no such source")
    expect(bank.transfer(5, "alice", "alice", 10), None, "same account")
    expect(peek(bank, 6, "alice"), 100, "nothing moved")


@case("a transfer may empty an account exactly")
def transfer_to_zero(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "alice", 300)
    expect(bank.transfer(4, "alice", "bob", 300), 0)
    expect(bank.transfer(5, "alice", "bob", 1), None, "nothing left to send")
