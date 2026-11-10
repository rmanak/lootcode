Customers want to set up payments that go out later — a bill that is due next
week, a transfer to a landlord at the end of the month — so implement
operations to schedule a payment, cancel it while it is still waiting, and
check what became of it.

```python
schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str | None
```

should schedule a payment of `amount` from the account `account_id`, to be
carried out at `timestamp + delay`. Returns a unique identifier for the
scheduled payment, or `None` if `account_id` doesn't exist. Payment
identifiers are `"payment1"` for the first payment the bank schedules,
`"payment2"` for the second, and so on — a single counter shared by the whole
bank. A rejected call does not use up a number.

Scheduling does not check the balance: an account may schedule more than it
currently holds. It is guaranteed that `delay` is a positive integer.

When a scheduled payment falls due, it is carried out as follows:

- Scheduled payments are processed **before any other operation** at the same
  timestamp. A payment falls due at its timestamp even if no operation happens
  to be called then, so any operation at or after that moment must already see
  its effect.
- If several payments fall due before an operation, they are processed in
  order of their due time; payments due at the same moment are processed in
  the order they were scheduled.
- If the account has enough money at that moment, the amount is withdrawn and
  the payment becomes `"EXECUTED"`. An account may pay out its entire balance.
- If the account does not have enough money at that moment, the payment is
  **skipped**: nothing is withdrawn, the payment becomes `"SKIPPED"`, and it is
  never retried.

```python
cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool
```

should cancel the scheduled payment with identifier `payment_id`. Returns
`True` if the payment was cancelled, or `False` otherwise. A call that returns
`False` changes nothing. Specifically:

- Returns `False` if `account_id` doesn't exist.
- Returns `False` if no payment with identifier `payment_id` exists, or it
  belongs to a different account.
- Returns `False` if the payment has already been executed, skipped or
  cancelled. Note that due payments are processed before the cancellation, so
  cancelling a payment at exactly its due timestamp fails.

```python
get_payment_status(self, timestamp: int, account_id: str, payment_id: str) -> str | None
```

should return the status of the payment `payment_id`: `"SCHEDULED"` while it
is waiting, then `"EXECUTED"`, `"SKIPPED"` or `"CANCELED"`. Returns `None` if
`account_id` doesn't exist, if no payment with identifier `payment_id` exists,
or if the payment belongs to a different account.

How the existing operations change:

- `top_spenders` now also counts the amount of every **executed** scheduled
  payment in its account's outgoing total, from the moment it is carried out.
  Payments that are still waiting, skipped or cancelled count for nothing.
- Every operation, including `deposit`, `transfer` and `top_spenders`, first
  processes the payments that are due at or before its timestamp.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.deposit(3, "alice", 100)` | returns `100` |
| `p1 = bank.schedule_payment(4, "alice", 30, 10)` | returns `"payment1"`; due at 4 + 10 = 14 |
| `p2 = bank.schedule_payment(5, "alice", 90, 10)` | returns `"payment2"`; due at 15; alice can't afford both, but scheduling never checks the balance |
| `p3 = bank.schedule_payment(6, "alice", 5, 20)` | returns `"payment3"`; due at 26 |
| `bank.schedule_payment(7, "carol", 10, 5)` | returns `None`; there is no account `"carol"`, and no id is used up |
| `bank.get_payment_status(8, "alice", p1)` | returns `"SCHEDULED"` |
| `bank.get_payment_status(9, "bob", p1)` | returns `None`; the payment belongs to alice |
| `bank.cancel_payment(10, "alice", p3)` | returns `True` |
| `bank.get_payment_status(14, "alice", p1)` | returns `"EXECUTED"`; `"payment1"` was carried out at timestamp 14, before this call; balances: `{"alice": 70, "bob": 0}` |
| `bank.cancel_payment(15, "alice", p2)` | returns `False`; `"payment2"` fell due at 15 and was processed before the cancel — alice had only 70 of the 90, so it was skipped |
| `bank.get_payment_status(16, "alice", p2)` | returns `"SKIPPED"` |
| `bank.top_spenders(17, 2)` | returns `["alice(30)", "bob(0)"]`; only the executed payment counts as spending |
| `bank.cancel_payment(18, "alice", p3)` | returns `False`; it is already cancelled |
| `bank.deposit(30, "alice", 1)` | returns `71`; the cancelled payment never ran; balances: `{"alice": 71, "bob": 0}` |
