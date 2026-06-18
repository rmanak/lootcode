Given `tokens` representing an arithmetic expression in Reverse Polish Notation,
evaluate it and return **the integer result**. Valid operators are `+`, `-`, `*`,
`/`; division truncates toward zero. Each operand and intermediate result fits in
a signed 64-bit integer.

## Constraints
- `1 <= len(tokens) <= 10^4`.
- Each token is an operator or an integer in `[-2*10^4, 2*10^4]`.
- The expression is always valid.

## Examples
Input: `tokens = ["2","1","+","3","*"]`
Output: `9`
Explanation: `((2 + 1) * 3) = 9`.

Input: `tokens = ["4","13","5","/","+"]`
Output: `6`
Explanation: `(4 + (13 / 5)) = 6`.

Input: `tokens = ["10","6","9","3","+","-11","*","/","*","17","+","5","+"]`
Output: `22`
