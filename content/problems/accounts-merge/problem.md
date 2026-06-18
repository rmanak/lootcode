Each entry in `accounts` is `[name, email1, email2, ...]`. Two accounts belong to
the same person if they share **at least one email** (names may repeat across
different people). Merge all accounts of the same person and return **the merged
accounts**. Within each merged account put the name first, then its emails in
**sorted order**. The accounts themselves may be returned **in any order**.

## Constraints
- `1 <= len(accounts) <= 1000`; each account has a name and at least one email.
- Emails are lowercase and unique within an account.

## Examples
Input: `accounts = [["John","a@m.com","b@m.com"],["John","b@m.com","c@m.com"],["Mary","x@m.com"]]`
Output: `[["John","a@m.com","b@m.com","c@m.com"],["Mary","x@m.com"]]`
Explanation: the two John accounts share `b@m.com`.

Input: `accounts = [["A","a@m.com"]]`
Output: `[["A","a@m.com"]]`

Input: `accounts = [["A","a@m.com"],["B","b@m.com"]]`
Output: `[["A","a@m.com"],["B","b@m.com"]]`
