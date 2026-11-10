### Instructions

Your task is to implement a simplified version of a banking system. A bank
keeps accounts that hold money: customers open an account, put money in, take
it out, and send it to each other. Some transfers need the recipient's
confirmation before they complete, and until then the money is set aside. The
system you are building is the ledger behind all of that. Everything is kept in
memory, and every operation carries the timestamp at which it happens.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `Bank`. Plan your design according to the level
specifications below:

- **Level 1:** The banking system should support creating accounts, depositing
  and withdrawing money, and reading balances.
- **Level 2:** The banking system should support transfers between accounts,
  and ranking accounts by how much money has moved through them.
- **Level 3:** The banking system should support transfers that hold the money
  until the recipient accepts them, and expire if they are not accepted in
  time.
- **Level 4:** The banking system should support merging two accounts into one,
  and listing an account's transaction history.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so plan a data model you can extend rather than one you will have to replace.

### Notes

- Timestamps are non-negative integers measured in milliseconds, and they
  strictly increase from one call to the next within a test.
- Amounts are positive whole numbers, and balances are always whole numbers.
- An account can never go below zero: an operation that the account cannot
  afford is rejected and changes nothing.
- Account ids are case-sensitive strings.
- A fresh `Bank()` has no accounts.
