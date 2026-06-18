Evaluate the arithmetic expression `s` containing non-negative integers and the
operators `+`, `-`, `*`, `/` (no parentheses), respecting normal precedence.
Integer division **truncates toward zero**. Return the integer result.

## Constraints
- `1 <= len(s) <= 3*10^5`
- `s` is a valid expression; division is never by zero

## Examples
Input: `s = "3+2*2"`
Output: `7`
Explanation: `2*2` is evaluated first.

Input: `s = " 3/2 "`
Output: `1`
Explanation: `3/2` truncates to `1`.
