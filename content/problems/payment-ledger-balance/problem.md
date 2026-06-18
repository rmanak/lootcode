Each transaction `[from, to, amount]` moves `amount` from account `from` to account
`to`. Return a map from every account that appears to its **net balance** (incoming
minus outgoing).

## Constraints
- `0 <= len(transactions) <= 2*10^5`
- identifiers are non-empty strings; amounts fit in a signed 64-bit integer

## Examples
Input: `transactions = [["a","b",5],["b","c",2]]`
Output: `{"a":-5,"b":3,"c":2}`
Explanation: `a` pays 5; `b` receives 5 and pays 2 (net +3); `c` receives 2.

Input: `transactions = []`
Output: `{}`
Explanation: With no transactions, no account has a balance.
