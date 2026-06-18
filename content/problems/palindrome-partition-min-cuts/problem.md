Return the **minimum number of cuts** needed to partition `s` so that every part is
a palindrome.

## Constraints
- `1 <= len(s) <= 2000`
- `s` is lowercase letters

## Examples
Input: `s = "aab"`
Output: `1`
Explanation: One cut gives `"aa" | "b"`, both palindromes.

Input: `s = "a"`
Output: `0`
Explanation: A single character is already a palindrome.
