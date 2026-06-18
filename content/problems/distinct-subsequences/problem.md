Return the number of **distinct subsequences** of `s` that equal `t`. (A subsequence
keeps relative order but may drop characters.)

## Constraints
- `0 <= len(s), len(t) <= 1000`
- The answer fits in a 64-bit integer.

## Examples
Input: `s = "rabbbit", t = "rabbit"`
Output: `3`
Explanation: Drop any one of the three middle `b`s.

Input: `s = "babgbag", t = "bag"`
Output: `5`
Explanation: There are five ways to pick `b`, `a`, `g` in order.
