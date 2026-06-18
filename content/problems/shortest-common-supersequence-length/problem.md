Return the **length of the shortest string** that has both `str1` and `str2` as
subsequences.

## Constraints
- `1 <= len(str1), len(str2) <= 1000`
- both strings are lowercase letters

## Examples
Input: `str1 = "abac", str2 = "cab"`
Output: `5`
Explanation: `cabac` is a shortest common supersequence and has length `5`.

Input: `str1 = "aaaaaaaa", str2 = "aaaaaaaa"`
Output: `8`
Explanation: The identical strings are their own supersequence.
