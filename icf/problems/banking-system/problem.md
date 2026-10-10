### Instructions

Your task is to implement a simplified version of a banking system. A bank
keeps accounts that hold money: customers open an account, put money into it,
send money to each other, and pay for things with it. The system you are
building is the ledger behind all of that — it keeps every balance correct and
can answer questions about where the money went. Everything is kept in memory,
and every operation carries the timestamp at which it happens.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `Bank`. Plan your design according to the level
specifications below:

- **Level 1:** The banking system should support creating accounts, depositing
  money, and transferring money between accounts.
- **Level 2:** The banking system should support ranking accounts by how much
  money has left them.
- **Level 3:** The banking system should support payments that earn cashback a
  day later, and checking the status of a payment.
- **Level 4:** The banking system should support merging two accounts into one,
  and looking up what an account's balance was at an earlier moment.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### Notes

- Timestamps are non-negative integers measured in milliseconds, and they
  strictly increase from one call to the next within a test. The only
  exception is the `time_at` argument introduced in level 4, which names a
  moment in the past.
- Amounts are positive whole numbers, and balances are always whole numbers.
- An account can never go below zero: a transfer or payment that the account
  cannot afford is rejected and changes nothing.
- A fresh `Bank()` has no accounts.
