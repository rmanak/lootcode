The banking system should allow customers to pay for purchases directly from
their accounts, with a small cashback reward on every payment, and to check
whether that cashback has arrived yet.

```python
pay(self, timestamp: int, account_id: str, amount: int) -> str | None
```

should withdraw the given amount of money from the specified account and
return a unique identifier for the payment transaction. Payment identifiers
are `"payment1"` for the first successful payment the bank processes,
`"payment2"` for the second, and so on — a single counter shared by the whole
bank. A rejected payment does not use up a number.

Every successful payment earns a **2% cashback**. The cashback amount,
`amount * 0.02` rounded down to the nearest integer, is refunded to the account
24 hours after the payment. The waiting period is
24 * 60 * 60 * 1000 = 86400000 milliseconds (the unit of timestamps), so the
cashback is refunded at `timestamp + 86400000`. It is refunded at that moment
even if no operation happens to be called then, so any operation at or after
that timestamp must already see it. A payment too small to earn any cashback
(for example `amount = 40`, which earns 0) still succeeds.

Additional conditions:

- Returns `None` if `account_id` doesn't exist.
- Returns `None` if `account_id` has insufficient funds to perform the payment.
- `top_spenders` should now also count the money withdrawn by payments in each
  account's outgoing total. The cashback that is refunded later does not reduce
  that total.

```python
get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None
```

should return the status of the payment transaction with identifier `payment`.
Specifically:

- Returns `"IN_PROGRESS"` if the cashback for the payment has not been
  refunded yet.
- Returns `"CASHBACK_RECEIVED"` if the cashback has been refunded — that is,
  from the payment's timestamp + 86400000 onward.
- Returns `None` if `account_id` doesn't exist.
- Returns `None` if no payment with identifier `payment` exists.
- Returns `None` if the payment was made from an account other than
  `account_id`.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `DAY = 86_400_000` | 24 hours in milliseconds, to keep the timestamps readable |
| `bank = Bank()` | a new bank with no accounts |
| `bank.create_account(1, "alice")` | returns `True` |
| `bank.create_account(2, "bob")` | returns `True` |
| `bank.deposit(3, "alice", 2000)` | returns `2000` |
| `payment = bank.pay(4, "alice", 1049)` | returns `"payment1"`; balances: `{"alice": 951, "bob": 0}`; 2% of 1049 is 20.98, so a cashback of 20 is due at timestamp 4 + 86400000 |
| `bank.pay(5, "alice", 10000)` | returns `None`; alice doesn't have enough money, and no payment id is used up |
| `bank.deposit(6, "bob", 100)` | returns `100` |
| `bank.pay(7, "bob", 40)` | returns `"payment2"`; 2% of 40 is 0.8, so the cashback is 0; balances: `{"alice": 951, "bob": 60}` |
| `bank.get_payment_status(8, "alice", payment)` | returns `"IN_PROGRESS"` |
| `bank.get_payment_status(9, "bob", payment)` | returns `None`; `"payment1"` was made from alice's account, not bob's |
| `bank.get_payment_status(10, "alice", "payment7")` | returns `None`; there is no such payment |
| `bank.top_spenders(11, 2)` | returns `["alice(1049)", "bob(40)"]`; payments count as outgoing money |
| `bank.get_payment_status(4 + DAY - 1, "alice", payment)` | returns `"IN_PROGRESS"`; one millisecond before the cashback is due |
| `bank.get_payment_status(4 + DAY, "alice", payment)` | returns `"CASHBACK_RECEIVED"`; the 20 has been refunded; balances: `{"alice": 971, "bob": 60}` |
| `bank.top_spenders(4 + DAY + 1, 2)` | returns `["alice(1049)", "bob(40)"]`; the refunded cashback does not reduce alice's total |
| `bank.get_payment_status(7 + DAY, "bob", "payment2")` | returns `"CASHBACK_RECEIVED"`; a cashback of 0 still completes on time |
