Remove the **minimum** number of parentheses to make `s` a valid parenthesization,
and return **all** distinct strings achievable with that minimum number of removals.
The answer may be returned in any order; characters other than `(` and `)` are never
removed.

## Constraints
- `0 <= len(s) <= 25`
- `s` consists of lowercase letters and the characters `(` and `)`

## Examples
Input: `s = "()())()"`
Output: `["(())()","()()()"]`
Explanation: Removing one `)` yields these two valid strings.

Input: `s = ")("`
Output: `[""]`
Explanation: Both parentheses must be removed.
