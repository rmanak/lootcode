You are given a string `s` of uppercase English letters and an integer `k`. You may
pick **at most `k`** positions in `s` and replace each with any uppercase letter.

Return **the length of the longest substring made of a single repeated letter** you
can obtain after performing at most `k` replacements.

## Constraints
- `1 <= len(s) <= 10^5`
- `s` consists of uppercase English letters only.
- `0 <= k <= len(s)`

## Examples
Input: `s = "ABAB", k = 2`
Output: `4`
Explanation: Replace the two `A`s with `B`s (or vice versa) to get `"BBBB"`.

Input: `s = "AABABBA", k = 1`
Output: `4`
Explanation: Replace the middle `A` with `B` to get `"AABBBBA"`; the run `"BBBB"` has length 4.
