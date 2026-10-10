The bank wants to identify the customers who are not keeping their money in
their accounts, so implement an operation to rank accounts by their **outgoing
transactions** — the total amount of money that has left each account.

```python
top_spenders(self, timestamp: int, n: int) -> list[str]
```

should return the identifiers of the top `n` accounts with the highest outgoing
totals, sorted in descending order of that total. If two accounts have the same
total, the one whose `account_id` comes first alphabetically is listed first.
The result should be a list of strings in the following format:

```
["<account_id_1>(<total_outgoing_1>)", "<account_id_2>(<total_outgoing_2>)", ..., "<account_id_n>(<total_outgoing_n>)"]
```

Additional conditions:

- An account's outgoing total is the sum of all the money it has successfully
  transferred out. Deposits, incoming transfers and rejected transfers never
  count. (The `pay` operation introduced in level 3 will add to this total as
  well.)
- Every account appears in the ranking, including accounts that have never
  sent anything — their total is `0`.
- If fewer than `n` accounts exist, return all of them. If `n` is `0`, or the
  bank has no accounts, return an empty list.
- "Alphabetically" means ordinary string comparison, so `"Zed"` comes before
  `"amy"` and `"10"` comes before `"9"`.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.create_account(3, "carol")` | returns `True` |
| `bank.deposit(4, "alice", 1000)` | returns `1000` |
| `bank.deposit(5, "bob", 1000)` | returns `1000` |
| `bank.deposit(6, "carol", 1000)` | returns `1000` |
| `bank.transfer(7, "alice", "bob", 300)` | returns `700`; alice has sent 300 |
| `bank.transfer(8, "bob", "carol", 300)` | returns `1000`; bob has sent 300 |
| `bank.transfer(9, "carol", "alice", 500)` | returns `800`; carol has sent 500 |
| `bank.transfer(10, "alice", "bob", 5000)` | returns `None`; a rejected transfer adds nothing to alice's total |
| `bank.top_spenders(11, 2)` | returns `["carol(500)", "alice(300)"]` |
| `bank.top_spenders(12, 10)` | returns `["carol(500)", "alice(300)", "bob(300)"]`; alice and bob are tied at 300, so they are ordered by id, and only three accounts exist |
| `bank.create_account(13, "dave")` | returns `True` |
| `bank.top_spenders(14, 4)` | returns `["carol(500)", "alice(300)", "bob(300)", "dave(0)"]`; dave has sent nothing but still appears |
| `bank.top_spenders(15, 0)` | returns `[]` |
