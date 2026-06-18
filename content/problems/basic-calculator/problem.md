Evaluate the arithmetic expression `s` containing non-negative integers, `+`, `-`,
parentheses, and spaces, and return its integer value. (`-` is the binary subtraction
operator and may follow `(`.)

## Constraints
- `1 <= len(s) <= 3*10^5`
- `s` is a valid expression of digits, `+`, `-`, `(`, `)`, and spaces

## Examples
Input: `s = "1 + (2 - 3)"`
Output: `0`
Explanation: The parenthesized part is `-1`.

Input: `s = "(1+(4+5+2)-3)+(6+8)"`
Output: `23`
Explanation: Evaluates left to right respecting parentheses.
