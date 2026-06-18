Given two strings `word1` and `word2`, return **the minimum number of single-
character insertions, deletions, and substitutions** needed to transform `word1`
into `word2` (the Levenshtein distance).

## Constraints
- `0 <= len(word1), len(word2) <= 500`.
- Strings contain lowercase English letters.

## Examples
Input: `word1 = "horse", word2 = "ros"`
Output: `3`
Explanation: horse → rorse → rose → ros.

Input: `word1 = "intention", word2 = "execution"`
Output: `5`

Input: `word1 = "", word2 = "abc"`
Output: `3`
