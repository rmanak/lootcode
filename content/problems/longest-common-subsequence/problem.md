Given strings `text1` and `text2`, return **the length of their longest common
subsequence**, or `0` if there is none. A subsequence keeps relative order but may
drop characters.

## Constraints
- `1 <= len(text1), len(text2) <= 1000`
- both consist of lowercase English letters

## Examples
Input: `text1 = "abcde", text2 = "ace"`
Output: `3`
Explanation: the LCS is `"ace"`.

Input: `text1 = "abc", text2 = "abc"`
Output: `3`

Input: `text1 = "abc", text2 = "def"`
Output: `0`
