Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all
overlapping intervals and return **the merged intervals sorted by start**. Intervals
that touch at an endpoint (e.g. `[1,4]` and `[4,5]`) are considered overlapping.

## Constraints
- `1 <= len(intervals) <= 10^4`
- `intervals[i].length == 2`
- `0 <= start_i <= end_i <= 10^4`

## Examples
Input: `intervals = [[1,3],[2,6],[8,10],[15,18]]`
Output: `[[1,6],[8,10],[15,18]]`
Explanation: `[1,3]` and `[2,6]` overlap, so they merge into `[1,6]`.

Input: `intervals = [[1,4],[4,5]]`
Output: `[[1,5]]`

Input: `intervals = [[4,7],[1,4]]`
Output: `[[1,7]]`
