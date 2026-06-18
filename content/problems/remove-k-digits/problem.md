Given a non-negative integer as the string `num`, remove exactly `k` digits so the
resulting number is as **small as possible**. Return it as a string with no leading
zeros (use `"0"` if everything is removed or the result is zero).

## Constraints
- `1 <= len(num) <= 10^5`
- `0 <= k <= len(num)`
- `num` has no leading zeros (except `num == "0"`)

## Examples
Input: `num = "1432219", k = 3`
Output: `"1219"`
Explanation: Drop `4`, `3`, and one `2`.

Input: `num = "10", k = 2`
Output: `"0"`
Explanation: Removing both digits leaves `0`.
