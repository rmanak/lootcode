Given an encoded string `s` using the rule `k[encoded]` (the bracketed part is
repeated `k` times, and encodings may be nested), return **the decoded string**.

## Constraints
- `1 <= len(s) <= 3*10^4`; decoded length fits comfortably in memory.
- `s` contains lowercase letters, digits, and the brackets `[` `]`.
- Digits only appear as repeat counts `k` with `1 <= k <= 300`.

## Examples
Input: `s = "3[a]2[bc]"`
Output: `"aaabcbc"`

Input: `s = "3[a2[c]]"`
Output: `"accaccacc"`

Input: `s = "2[abc]3[cd]ef"`
Output: `"abcabccdcdcdef"`
