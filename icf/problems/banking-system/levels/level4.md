The banking system should support merging two accounts into one — for example,
when two customers decide to combine their finances — while retaining both
accounts' money, spending and payments. It should also be able to report what
an account's balance was at any earlier moment.

```python
merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool
```

should merge `account_id_2` into `account_id_1`. Returns `True` if the accounts
were successfully merged, or `False` otherwise. A merge that returns `False`
changes nothing. Specifically:

- Returns `False` if `account_id_1` is equal to `account_id_2`.
- Returns `False` if `account_id_1` or `account_id_2` doesn't exist.
- The balance of `account_id_2` should be added to the balance of
  `account_id_1`.
- `top_spenders` should recognize merged accounts — the outgoing total of
  `account_id_1` becomes the sum of all the money transferred and paid out of
  both accounts.
- All pending cashback refunds for `account_id_2` should still be processed at
  their original times, but refunded to `account_id_1` instead.
- After the merge, it must be possible to check the status of payments made by
  `account_id_2` by passing `account_id_1` as the `account_id`.
- `account_id_2` should be removed from the system after the merge. Its
  identifier becomes free: a later `create_account` with that identifier
  creates a brand-new, empty account that inherits nothing from the account
  that was merged away.

Merges can chain: if `"a"` absorbs `"b"`, and later `"c"` absorbs `"a"`, then
everything that belonged to `"b"` — its money, its spending, its payments and
its pending cashback — ends up with `"c"`.

```python
get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None
```

should return the total amount of money in the account `account_id` at the
moment `time_at`, which is never later than `timestamp`. Specifically:

- If an operation was processed at exactly `time_at`, the result reflects the
  balance after that operation.
- A cashback counts from the moment it is refunded (the payment's timestamp +
  86400000), not from the moment the payment was made.
- Returns `None` if `account_id` doesn't exist now — including an account that
  was merged away, whatever `time_at` is.
- Returns `None` if the account did not exist yet at `time_at`. An account
  exists from the timestamp of its `create_account` call, starting with a
  balance of `0`.
- An identifier that was merged away and then created again refers only to the
  new account: moments before the new account was created return `None`.
- For the account that absorbed another one, moments before the merge return
  that account's own balance at the time; the merged-in money counts from the
  merge onward.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.deposit(3, "alice", 100)` | returns `100` |
| `bank.deposit(4, "bob", 50)` | returns `50` |
| `bank.get_balance(5, "alice", 1)` | returns `0`; alice was created at 1, before any deposit |
| `bank.get_balance(6, "alice", 3)` | returns `100`; the deposit at timestamp 3 is included |
| `bank.get_balance(7, "alice", 0)` | returns `None`; alice did not exist yet at timestamp 0 |
| `bank.merge_accounts(8, "alice", "bob")` | returns `True`; bob is merged into alice; balances: `{"alice": 150}` |
| `bank.merge_accounts(9, "alice", "bob")` | returns `False`; bob no longer exists |
| `bank.get_balance(10, "alice", 8)` | returns `150` |
| `bank.get_balance(11, "alice", 4)` | returns `100`; before the merge, alice's account held only its own money |
| `bank.get_balance(12, "bob", 4)` | returns `None`; bob was merged away |
| `bank.create_account(13, "bob")` | returns `True`; the id is free again; balances: `{"alice": 150, "bob": 0}` |
| `bank.get_balance(14, "bob", 4)` | returns `None`; the new bob did not exist at timestamp 4 |
| `bank.get_balance(15, "bob", 13)` | returns `0` |

The next example shows a payment and its pending cashback following the money
into the absorbing account:

| Query | Explanation |
|---|---|
| `DAY = 86_400_000` | 24 hours in milliseconds |
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.deposit(3, "bob", 1000)` | returns `1000` |
| `payment = bank.pay(4, "bob", 500)` | returns `"payment1"`; a cashback of 10 is due at 4 + 86400000 |
| `bank.merge_accounts(5, "alice", "bob")` | returns `True`; balances: `{"alice": 500}` |
| `bank.get_payment_status(6, "alice", payment)` | returns `"IN_PROGRESS"`; alice can now look up bob's payment |
| `bank.get_payment_status(7, "bob", payment)` | returns `None`; bob no longer exists |
| `bank.top_spenders(8, 1)` | returns `["alice(500)"]`; alice inherited bob's spending |
| `bank.get_balance(4 + DAY, "alice", 4 + DAY)` | returns `510`; the cashback was refunded to alice |
| `bank.get_payment_status(4 + DAY + 1, "alice", payment)` | returns `"CASHBACK_RECEIVED"` |
