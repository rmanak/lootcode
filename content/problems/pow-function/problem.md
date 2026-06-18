Given a floating-point number `x` and an integer `n` (possibly negative), compute
`x` raised to the power `n` and return the result **rounded to 6 decimal places**.
Aim for `O(log n)` multiplications (fast exponentiation).

## Constraints
- `-30.0 <= x <= 30.0`, `-30 <= n <= 30`.
- `x != 0` when `n < 0`.

## Examples
Input: `x = 2.0, n = 10`
Output: `1024.0`

Input: `x = 2.1, n = 3`
Output: `9.261`

Input: `x = 2.0, n = -2`
Output: `0.25`
