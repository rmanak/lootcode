Replay `operations` and return **the list of results**. Each operation is
`["hit", t]` recording a hit at timestamp `t` (returns `null`), or
`["getHits", t]` returning the number of hits in the **past 300 seconds**, i.e.
with timestamp in `(t-300, t]`. Timestamps are non-decreasing across operations.

## Constraints
- `1 <= len(operations) <= 10^5`; timestamps are monotonically non-decreasing.
- `1 <= t <= 2*10^9`.

## Examples
Input: `operations = [["hit",1],["hit",2],["hit",3],["getHits",4],["hit",300],["getHits",300],["getHits",301]]`
Output: `[null,null,null,3,null,4,3]`

Input: `operations = [["hit",1],["getHits",1]]`
Output: `[null,1]`

Input: `operations = [["getHits",100]]`
Output: `[0]`
