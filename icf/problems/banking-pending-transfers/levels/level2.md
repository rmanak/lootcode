Customers want to send money to each other, and the bank wants to know which
accounts are the busiest. Implement transfers between accounts, and a ranking
of accounts by their **activity** — the total amount of money that has moved
into or out of each account.

```python
transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None
```

should move `amount` from account `source_id` to account `target_id`
immediately. Returns the balance of `source_id` after the transfer, or `None`
otherwise, in which case nothing changes. Specifically:

- Returns `None` if `source_id` or `target_id` doesn't exist.
- Returns `None` if `source_id` and `target_id` are the same account.
- Returns `None` if `source_id` holds less than `amount`.

```python
top_activity(self, timestamp: int, n: int) -> list[str]
```

should return the top `n` accounts by activity, in the following format:

```
["<account_id_1>(<activity_1>)", "<account_id_2>(<activity_2>)", ..., "<account_id_n>(<activity_n>)"]
```

Additional conditions:

- An account's activity is the sum of the amounts of all its successful
  deposits, withdrawals and transfers — money in and money out both count,
  so a transfer adds its amount to the activity of **both** accounts. Refused
  operations count for nothing.
- Accounts are sorted in descending order of activity or, in the case of ties,
  by `account_id` in ordinary string order (`"B"` comes before `"a"`).
- Every account appears, including accounts with no activity.
- If fewer than `n` accounts exist, return all of them. If `n` is `0`, or the
  bank has no accounts, return an empty list.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.create_account(3, "carol")` | returns `True` |
| `bank.deposit(4, "alice", 300)` | returns `300`; alice's activity: 300 |
| `bank.transfer(5, "alice", "bob", 100)` | returns `200`; alice's balance after the transfer; activity: alice 400, bob 100 |
| `bank.transfer(6, "bob", "bob", 10)` | returns `None`; an account cannot transfer to itself |
| `bank.transfer(7, "bob", "carol", 500)` | returns `None`; bob only has 100 |
| `bank.withdraw(8, "bob", 50)` | returns `50`; activity: bob 150 |
| `bank.top_activity(9, 2)` | returns `["alice(400)", "bob(150)"]` |
| `bank.top_activity(10, 5)` | returns `["alice(400)", "bob(150)", "carol(0)"]`; carol has no activity but still appears |
