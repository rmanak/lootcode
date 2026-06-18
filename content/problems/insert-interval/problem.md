You are given non-overlapping `intervals` sorted by start, and a `newInterval`.
**Insert `newInterval`, merging as needed, and return the resulting sorted list of
non-overlapping intervals.** You may build and return a new list.

## Constraints
- `0 <= len(intervals) <= 10^4`
- `intervals[i].length == 2`, `newInterval.length == 2`
- `0 <= start_i <= end_i <= 10^5` and `0 <= start <= end <= 10^5`
- `intervals` is sorted by start in ascending order.

## Examples
Input: `intervals = [[1,3],[6,9]], newInterval = [2,5]`
Output: `[[1,5],[6,9]]`

Input: `intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]`
Output: `[[1,2],[3,10],[12,16]]`
Explanation: `[4,8]` overlaps `[3,5]`, `[6,7]`, and `[8,10]`.
