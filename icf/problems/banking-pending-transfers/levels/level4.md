The banking system should support merging two accounts into one — for example,
when two customers decide to combine their finances — keeping both accounts'
money, activity and transactions. It should also be able to list the
transactions an account has made.

```python
merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool
```

should merge `account_id_2` into `account_id_1`. Returns `True` if the accounts
were merged, or `False` otherwise. A merge that returns `False` changes
nothing. Specifically:

- Returns `False` if `account_id_1` is equal to `account_id_2`.
- Returns `False` if `account_id_1` or `account_id_2` doesn't exist.
- The balance of `account_id_2` is added to the balance of `account_id_1`, and
  so is its activity.
- Pending transfers that `account_id_2` initiated stay pending: if they are
  accepted, the transfer is recorded as `account_id_1`'s; if they expire, the
  held money returns to `account_id_1`.
- Pending transfers addressed to `account_id_2` can now be accepted by
  `account_id_1`.
- A pending transfer **between** the two accounts (in either direction) would
  become a transfer from an account to itself, so it is cancelled: its held
  money returns to `account_id_1` at the merge, and it can no longer be
  accepted.
- `account_id_2` is removed from the system. Its identifier becomes free: a
  later `create_account` with that identifier creates a brand-new, empty
  account that inherits nothing — no balance, no activity, no history, and no
  pending transfers to accept.

Merges can chain: if `"a"` absorbs `"b"`, and later `"c"` absorbs `"a"`, then
everything that belonged to `"b"` ends up with `"c"`.

```python
get_history(self, timestamp: int, account_id: str) -> list[str] | None
```

should return the account's completed transactions, in the order they
happened, each as a string `"<timestamp>:<type>:<amount>"`, where `<type>` is
one of:

- `deposit` and `withdraw`;
- `transfer_out` and `transfer_in` — a transfer, recorded on both accounts, at
  the moment it completes: immediately for `transfer`, and at the moment of
  acceptance for a pending transfer.

Returns `None` if the account doesn't exist. Additional conditions:

- Pending transfers, expired transfers and cancelled transfers are not
  transactions and never appear. Neither do refused operations.
- After a merge, the history of `account_id_1` contains the transactions of
  both accounts, in the order they happened. Transactions recorded at the same
  timestamp keep the order in which they were recorded, so a transfer between
  the two accounts lists its `transfer_out` before its `transfer_in`.
- The sum of the amounts in an account's history is its activity.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.create_account(3, "carol")` | returns `True` |
| `bank.deposit(4, "bob", 100)` | returns `100` |
| `bank.transfer(5, "bob", "alice", 30)` | returns `70` |
| `t1 = bank.initiate_transfer(6, "bob", "carol", 50)` | returns `"transfer1"`; bob's 50 is held for carol |
| `t2 = bank.initiate_transfer(7, "alice", "bob", 10)` | returns `"transfer2"`; alice's 10 is held for bob |
| `bank.get_history(8, "bob")` | returns `["4:deposit:100", "5:transfer_out:30"]`; pending transfers are not in the history yet |
| `bank.merge_accounts(9, "alice", "bob")` | returns `True`; `"transfer2"` ran between the two accounts, so it is cancelled and alice gets the 10 back; bob's 50 stays held for carol |
| `bank.get_balance(10, "alice")` | returns `50`; alice's 20 + the 10 back + bob's 20 |
| `bank.accept_transfer(11, "alice", t2)` | returns `False`; `"transfer2"` was cancelled by the merge |
| `bank.accept_transfer(12, "carol", t1)` | returns `True`; the transfer bob started is now part of alice's account |
| `bank.get_history(13, "alice")` | returns `["4:deposit:100", "5:transfer_out:30", "5:transfer_in:30", "12:transfer_out:50"]`; both accounts' transactions, in the order they happened |
| `bank.top_activity(14, 3)` | returns `["alice(210)", "carol(50)"]` |
| `bank.get_history(15, "bob")` | returns `None`; bob no longer exists |
| `bank.create_account(16, "bob")` | returns `True`; the id is free again |
| `bank.get_history(17, "bob")` | returns `[]`; the new bob inherits nothing |
