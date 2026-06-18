Given a list of `words` sorted lexicographically by the rules of an unknown
alphabet, derive **a possible character order** as a string. If several orders are
valid, return the **lexicographically smallest** (using normal letter order to
break ties). Return the empty string `""` if the ordering is inconsistent (for
example a word precedes its own prefix).

## Constraints
- `1 <= len(words) <= 1000`; words contain lowercase English letters.

## Examples
Input: `words = ["wrt","wrf","er","ett","rftt"]`
Output: `"wertf"`

Input: `words = ["z","x"]`
Output: `"zx"`

Input: `words = ["z","x","z"]`
Output: `""`
Explanation: the constraints are contradictory.
