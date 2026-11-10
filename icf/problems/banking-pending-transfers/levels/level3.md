For larger payments, the recipient should confirm before the money arrives.
Implement **pending transfers**: the sender initiates a transfer, the money is
set aside straight away, and the transfer completes only when the recipient
accepts it. A transfer that is not accepted within 24 hours expires, and the
money goes back to the sender.

```python
initiate_transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> str | None
```

should start a pending transfer of `amount` from `source_id` to `target_id`.
The amount leaves the balance of `source_id` immediately — it is **held**, so
it can't be spent again — but it does not reach `target_id` yet. Returns a
unique identifier for the transfer: `"transfer1"` for the first pending
transfer the bank creates, `"transfer2"` for the second, and so on — a single
counter shared by the whole bank, which a refused call does not advance.
Returns `None` under the same conditions as `transfer`: either account doesn't
exist, they are the same account, or `source_id` holds less than `amount`.

A pending transfer **expires** 24 hours after it was initiated:
24 * 60 * 60 * 1000 = 86400000 milliseconds, so at `timestamp + 86400000`. At
that moment the held amount is returned to the balance of `source_id`. This
happens even if no operation happens to be called then, so any operation at or
after that moment must already see the money back.

```python
accept_transfer(self, timestamp: int, account_id: str, transfer_id: str) -> bool
```

should complete the pending transfer `transfer_id`: its amount is added to the
balance of the recipient. Returns `True` if the transfer was accepted, or
`False` otherwise, in which case nothing changes. Specifically:

- Returns `False` if `account_id` doesn't exist, or no transfer
  `transfer_id` exists.
- Returns `False` if `account_id` is not the recipient of the transfer.
  Only the recipient can accept.
- Returns `False` if the transfer has already been accepted, or has expired —
  including when accepting at exactly its expiry timestamp.

How the existing operations change:

- `top_activity` counts a pending transfer for both accounts only when it is
  accepted. A transfer that is still pending or has expired counts for
  nothing.
- `get_balance` and every check for sufficient funds see only the money that
  is not held.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `DAY = 86_400_000` | 24 hours in milliseconds |
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.deposit(3, "alice", 500)` | returns `500` |
| `t1 = bank.initiate_transfer(4, "alice", "bob", 200)` | returns `"transfer1"`; the 200 leaves alice's balance and is held |
| `bank.get_balance(5, "alice")` | returns `300` |
| `bank.get_balance(6, "bob")` | returns `0`; bob receives nothing until the transfer is accepted |
| `bank.withdraw(7, "alice", 400)` | returns `None`; held money cannot be spent |
| `t2 = bank.initiate_transfer(8, "alice", "bob", 100)` | returns `"transfer2"`; expires at 8 + DAY |
| `bank.accept_transfer(9, "alice", t1)` | returns `False`; only the recipient can accept |
| `bank.accept_transfer(10, "bob", t1)` | returns `True`; balances: `{"alice": 200, "bob": 200}` |
| `bank.accept_transfer(11, "bob", t1)` | returns `False`; already accepted |
| `bank.top_activity(12, 2)` | returns `["alice(700)", "bob(200)"]`; the accepted transfer counts for both; the pending one does not |
| `bank.accept_transfer(8 + DAY, "bob", t2)` | returns `False`; the transfer expired at exactly 8 + DAY |
| `bank.get_balance(8 + DAY + 1, "alice")` | returns `300`; the 100 that was held came back |
