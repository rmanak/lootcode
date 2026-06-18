Given meeting time intervals `[start, end)` (half-open), return **the minimum
number of rooms** required so that no two meetings sharing a room overlap. A
meeting ending exactly when another starts can reuse the room.

## Constraints
- `0 <= len(intervals) <= 10^4`.
- `0 <= start < end <= 10^9`.

## Examples
Input: `intervals = [[0,30],[5,10],[15,20]]`
Output: `2`

Input: `intervals = [[7,10],[2,4]]`
Output: `1`

Input: `intervals = [[1,5],[5,9],[9,12]]`
Output: `1`
