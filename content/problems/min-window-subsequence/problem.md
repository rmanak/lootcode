Return the **shortest contiguous substring** of `s` such that `t` is a subsequence
of it. If no such window exists, return `""`. If several windows tie for shortest,
return the one with the smallest starting index.

## Constraints
- `1 <= len(s) <= 2*10^4`
- `1 <= len(t) <= 100`

## Examples
Input: `s = "abcdebdde", t = "bde"`
Output: `"bcde"`
Explanation: `bcde` is the shortest window containing `b`, `d`, `e` in order.

Input: `s = "jmeqksfrsdcmsiwvaovztaqenprpvnbstl", t = "u"`
Output: `""`
Explanation: `u` never appears in `s`.
