Given an array `intervals` where `intervals[i] = [start_i, end_i]`, return **the
minimum number of intervals to remove** so that the rest are non-overlapping.

Intervals that only touch at a point are non-overlapping — e.g. `[1,2]` and `[2,3]`.

## Constraints
- `1 <= len(intervals) <= 10^5`
- `intervals[i].length == 2`
- `-5 * 10^4 <= start_i < end_i <= 5 * 10^4`

## Examples
Input: `intervals = [[1,2],[2,3],[3,4],[1,3]]`
Output: `1`
Explanation: Remove `[1,3]` and the rest are non-overlapping.

Input: `intervals = [[1,2],[1,2],[1,2]]`
Output: `2`
Explanation: Remove two copies of `[1,2]`.

Input: `intervals = [[1,2],[2,3]]`
Output: `0`
