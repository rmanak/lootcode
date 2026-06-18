Given strings `s` and `t`, return **the shortest substring of `s` that contains
every character of `t` (counting duplicates)**. If no such window exists, return
the empty string `""`.

## Constraints
- `1 <= len(s), len(t) <= 10^5`
- `s` and `t` consist of uppercase and lowercase English letters
- The answer is unique; when lengths tie, the leftmost window is returned

## Examples
Input: `s = "ADOBECODEBANC", t = "ABC"`
Output: `"BANC"`

Input: `s = "a", t = "a"`
Output: `"a"`

Input: `s = "a", t = "aa"`
Output: `""`
Explanation: `s` has a single `'a'`, so it cannot cover both.
