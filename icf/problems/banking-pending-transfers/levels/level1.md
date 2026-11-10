Initially, the banking system does not contain any accounts, so implement
operations to open an account, put money into it, take money out of it, and
check how much it holds.

```python
create_account(self, timestamp: int, account_id: str) -> bool
```

should create a new account with the given identifier and a balance of `0`.
Returns `True` if the account was created, or `False` if an account with
`account_id` already exists — in which case the existing account is left
exactly as it was.

```python
deposit(self, timestamp: int, account_id: str, amount: int) -> int | None
```

should add `amount` to the account. Returns the balance after the deposit, or
`None` if the account doesn't exist.

```python
withdraw(self, timestamp: int, account_id: str, amount: int) -> int | None
```

should take `amount` out of the account. Returns the balance after the
withdrawal, or `None` if the account doesn't exist or holds less than
`amount`; a refused withdrawal changes nothing. An account may withdraw its
entire balance, leaving it at exactly `0`.

```python
get_balance(self, timestamp: int, account_id: str) -> int | None
```

should return the current balance of the account, or `None` if it doesn't
exist.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "alice")` | returns `False`; the id `"alice"` is already taken |
| `bank.get_balance(3, "alice")` | returns `0`; a new account starts empty |
| `bank.deposit(4, "alice", 500)` | returns `500` |
| `bank.withdraw(5, "alice", 200)` | returns `300` |
| `bank.withdraw(6, "alice", 400)` | returns `None`; alice only has 300, so nothing changes |
| `bank.withdraw(7, "alice", 300)` | returns `0`; the whole balance may be withdrawn |
| `bank.deposit(8, "bob", 100)` | returns `None`; there is no account `"bob"` |
| `bank.get_balance(9, "bob")` | returns `None` |
