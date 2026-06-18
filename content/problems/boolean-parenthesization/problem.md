`expr` is a boolean expression of operands `T` (true) and `F` (false) separated by
operators `&` (and), `|` (or), and `^` (xor). Return the number of ways to fully
parenthesize `expr` so that it evaluates to **true**.

## Constraints
- `1 <= len(expr) <= 199` with an odd length (operands and operators alternate)
- operands are `T`/`F`; operators are `&`, `|`, `^`

## Examples
Input: `expr = "T|F&T"`
Output: `2`
Explanation: `T|(F&T)` and `(T|F)&T` both evaluate to true.

Input: `expr = "T^F"`
Output: `1`
Explanation: The only parenthesization is true.
