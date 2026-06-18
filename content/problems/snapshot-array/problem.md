Implement an array of `length` integers (initially `0`) and replay `operations`,
returning the list of results. Operations are `["set", index, value]` (returns
`null`), `["snap"]` (takes a snapshot and returns its id, starting at `0`), and
`["get", index, snap_id]` (returns the value at `index` in that snapshot).

## Constraints
- `1 <= length <= 5*10^4`, `1 <= len(operations) <= 5*10^4`
- snap ids passed to `get` are valid

## Examples
Input: `length = 3, operations = [["set",0,5],["snap"],["set",0,6],["get",0,0]]`
Output: `[null,0,null,5]`
Explanation: Snapshot `0` recorded value `5` at index `0`.

Input: `length = 1, operations = [["snap"],["get",0,0]]`
Output: `[0,0]`
Explanation: Unset entries default to `0`.
