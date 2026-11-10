Initially, the banking system does not contain any accounts, so implement
operations to allow account creation, deposits, and transfers between different
accounts. This is the core of the ledger — every later level builds on these
balances.

```python
create_account(self, timestamp: int, account_id: str) -> bool
```

should create a new account with the given identifier and a balance of `0`, if
an account with that identifier doesn't already exist. Returns `True` if the
account was successfully created, or `False` if an account with `account_id`
already exists — in which case the existing account is left exactly as it was.

```python
deposit(self, timestamp: int, account_id: str, amount: int) -> int | None
```

should add the given amount of money to the specified account. Returns the
balance of the account after the deposit has been processed, or `None` if the
account doesn't exist.

```python
transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None
```

should move the given amount of money from account `source_id` to account
`target_id`. Returns the balance of `source_id` after the transfer if it was
successful, or `None` otherwise. A transfer that returns `None` changes
nothing. Specifically:

- Returns `None` if `source_id` or `target_id` doesn't exist.
- Returns `None` if `source_id` and `target_id` are the same account.
- Returns `None` if `source_id` has insufficient funds to perform the transfer.

An account may transfer its entire balance, leaving it at exactly `0`.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True`; balances: `{"alice": 0}` |
| `bank.create_account(2, "alice")` | returns `False`; the id `"alice"` is already taken |
| `bank.create_account(3, "bob")` | returns `True`; balances: `{"alice": 0, "bob": 0}` |
| `bank.deposit(4, "alice", 500)` | returns `500`; balances: `{"alice": 500, "bob": 0}` |
| `bank.deposit(5, "carol", 100)` | returns `None`; there is no account `"carol"` |
| `bank.transfer(6, "alice", "bob", 200)` | returns `300`, which is alice's balance after the transfer; balances: `{"alice": 300, "bob": 200}` |
| `bank.transfer(7, "alice", "bob", 900)` | returns `None`; alice only has 300, so nothing changes |
| `bank.transfer(8, "alice", "alice", 10)` | returns `None`; an account cannot transfer money to itself |
| `bank.transfer(9, "bob", "alice", 200)` | returns `0`; the whole balance may be sent; balances: `{"alice": 500, "bob": 0}` |
