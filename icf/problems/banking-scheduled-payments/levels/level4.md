The banking system should support merging two accounts into one — for example,
when two customers decide to combine their finances — while keeping both
accounts' money, spending and scheduled payments. It should also be able to
report what the balance under an account identifier was at any earlier moment,
even for an account that has since been merged away.

```python
merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool
```

should merge `account_id_2` into `account_id_1`. Returns `True` if the accounts
were successfully merged, or `False` otherwise. A merge that returns `False`
changes nothing. Specifically:

- Returns `False` if `account_id_1` is equal to `account_id_2`.
- Returns `False` if `account_id_1` or `account_id_2` doesn't exist.
- The balance of `account_id_2` is added to the balance of `account_id_1`.
- `top_spenders` should recognize merged accounts — the outgoing total of
  `account_id_1` becomes the sum of both accounts' outgoing totals.
- Payments that `account_id_2` scheduled and that are still waiting now belong
  to `account_id_1`: they keep their identifiers and due times, they are paid
  from `account_id_1`'s balance (or skipped if it cannot afford them), and they
  can be cancelled or looked up by passing `account_id_1` as the `account_id`.
- `account_id_2` is removed from the system after the merge. Its identifier
  becomes free: a later `create_account` with that identifier creates a
  brand-new, empty account that inherits nothing — not the balance, not the
  spending, not the payments.

Merges can chain: if `"a"` absorbs `"b"`, and later `"c"` absorbs `"a"`, then
everything that belonged to `"b"` ends up with `"c"`.

```python
get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None
```

should return the balance of the account that held the identifier
`account_id` at the moment `time_at`, which is never later than `timestamp`.
Specifically:

- If an operation was processed at exactly `time_at`, the result reflects the
  balance after that operation. A scheduled payment counts from its due time.
- An account holds its identifier from the timestamp of its `create_account`
  call (starting with a balance of `0`) until the timestamp at which it is
  merged away, exclusive.
- Returns `None` if no account held `account_id` at `time_at`: before the
  identifier was first created, or from the moment its account was merged
  away until the identifier was created again.
- An identifier that was merged away and then created again names two
  different accounts at two different times: moments before the merge return
  the old account's balance, moments after the re-creation return the new one's.
- For the account that absorbed another one, moments before the merge return
  its own balance at the time; the merged-in money counts from the merge
  onward.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.deposit(3, "alice", 100)` | returns `100` |
| `bank.deposit(4, "bob", 50)` | returns `50` |
| `p1 = bank.schedule_payment(5, "bob", 120, 10)` | returns `"payment1"`; due at 15 — more than bob has |
| `bank.merge_accounts(6, "alice", "alice")` | returns `False`; an account cannot be merged with itself |
| `bank.merge_accounts(7, "alice", "bob")` | returns `True`; balances: `{"alice": 150}` |
| `bank.get_payment_status(8, "alice", p1)` | returns `"SCHEDULED"`; bob's payment now belongs to alice |
| `bank.get_payment_status(9, "bob", p1)` | returns `None`; bob no longer exists |
| `bank.get_balance(15, "alice", 15)` | returns `30`; the payment was carried out from alice's money: 150 - 120 |
| `bank.top_spenders(16, 1)` | returns `["alice(120)"]` |
| `bank.get_balance(17, "alice", 6)` | returns `100`; before the merge, alice held only its own money |
| `bank.get_balance(18, "bob", 4)` | returns `50`; bob's balance before the merge is still known |
| `bank.get_balance(19, "bob", 7)` | returns `None`; from the merge on, no account holds the id `"bob"` |
| `bank.create_account(20, "bob")` | returns `True`; the id is free again, and this is a brand-new account |
| `bank.get_balance(21, "bob", 20)` | returns `0` |
| `bank.get_balance(22, "bob", 4)` | returns `50`; at timestamp 4 the id belonged to the old account |
| `bank.get_balance(23, "bob", 10)` | returns `None`; between the merge and the re-creation |
| `bank.get_balance(24, "alice", 0)` | returns `None`; alice did not exist yet |
