Each `equations[i] = [a, b]` with `values[i]` means `a / b = values[i]`. For each
query `[x, y]` return `x / y` derived from the known ratios, or `-1.0` if it cannot
be determined. Round each answer to **5 decimal places**.

## Constraints
- `1 <= len(equations) <= 20`, all values are positive
- variables are lowercase strings

## Examples
Input: `equations = [["a","b"],["b","c"]], values = [2.0,3.0], queries = [["a","c"],["c","a"]]`
Output: `[6.0,0.16667]`
Explanation: `a/c = 2*3 = 6`; `c/a = 1/6 ≈ 0.16667`.

Input: `equations = [["a","b"]], values = [2.0], queries = [["a","e"]]`
Output: `[-1.0]`
Explanation: Variable `e` never appears, so the ratio is unknown.
