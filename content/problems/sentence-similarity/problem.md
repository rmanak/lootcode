Two words are similar if they are equal or connected **transitively** through the
synonym `pairs`. Return whether `sentence1` and `sentence2` are similar: they must
have the same length and each pair of corresponding words must be similar.

## Constraints
- `0 <= len(sentence1), len(sentence2) <= 1000`
- `0 <= len(pairs) <= 2000`

## Examples
Input: `s1 = ["great","acting"], s2 = ["fine","drama"], pairs = [["great","good"],["fine","good"],["acting","drama"]]`
Output: `true`
Explanation: `great~good~fine` and `acting~drama`.

Input: `s1 = ["great"], s2 = ["bad"], pairs = [["great","good"]]`
Output: `false`
Explanation: `bad` is in no synonym group with `great`.
