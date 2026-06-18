Implement matching of the **entire** string `s` against pattern `p`, where `.`
matches any single character and `*` matches zero or more of the **preceding**
element. The match must cover all of `s`.

## Constraints
- `0 <= len(s) <= 20`, `0 <= len(p) <= 30`
- `s` is lowercase letters; `p` is lowercase letters, `.`, and `*`
- every `*` has a valid preceding element

## Examples
Input: `s = "aab", p = "c*a*b"`
Output: `true`
Explanation: `c*` matches empty, `a*` matches `aa`, `b` matches `b`.

Input: `s = "mississippi", p = "mis*is*p*."`
Output: `false`
Explanation: No consistent way to consume the whole string.
