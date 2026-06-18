You manage `n` nodes `0..n-1` under a sequence of `operations`. Each operation is
`["union", a, b]` (connect `a` and `b`) or `["connected", a, b]` (query). Return
**a list of booleans, one per `connected` query in order**, indicating whether the
two nodes are in the same connected component at that moment.

## Constraints
- `1 <= n <= 10^4`, `1 <= len(operations) <= 10^5`.
- `0 <= a, b < n`.

## Examples
Input: `n = 5, operations = [["connected",0,1],["union",0,1],["connected",0,1]]`
Output: `[false, true]`

Input: `n = 3, operations = [["union",0,1],["union",1,2],["connected",0,2]]`
Output: `[true]`

Input: `n = 2, operations = [["connected",0,0]]`
Output: `[true]`
