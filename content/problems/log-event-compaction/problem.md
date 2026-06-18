Given `samples` as `[timestamp, state]` pairs in strictly increasing timestamp
order, **merge maximal runs of equal consecutive states** into intervals
`[start, end, state]`, where `start` and `end` are the first and last timestamps
of the run. Return the list of intervals in order.

## Constraints
- `1 <= len(samples) <= 10^5`; timestamps strictly increase.

## Examples
Input: `samples = [[0,"on"],[1,"on"],[2,"off"],[5,"off"],[6,"on"]]`
Output: `[[0,1,"on"],[2,5,"off"],[6,6,"on"]]`

Input: `samples = [[3,"a"]]`
Output: `[[3,3,"a"]]`

Input: `samples = [[0,"a"],[1,"b"],[2,"a"]]`
Output: `[[0,0,"a"],[1,1,"b"],[2,2,"a"]]`
