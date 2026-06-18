A digit string is decoded with the mapping `"1" -> 'A'`, `"2" -> 'B'`, …,
`"26" -> 'Z'`. Given a string `s` of digits, return **the number of ways to decode
it**. A `'0'` cannot begin a code, and some strings cannot be decoded at all
(return `0`).

## Constraints
- `1 <= len(s) <= 100`
- `s` contains only digits and may contain leading zeros

## Examples
Input: `s = "12"`
Output: `2`
Explanation: `"AB"` (1 2) or `"L"` (12).

Input: `s = "226"`
Output: `3`
Explanation: `"BZ"` (2 26), `"VF"` (22 6) or `"BBF"` (2 2 6).

Input: `s = "06"`
Output: `0`
Explanation: a leading zero is invalid.
