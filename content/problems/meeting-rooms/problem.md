Given an array of meeting time intervals `[start, end)` (half-open), determine
whether **a single person could attend all meetings** — i.e. no two meetings
overlap. A meeting ending exactly when another starts does **not** count as an
overlap (the endpoints touch but don't overlap).

Return `True` if all meetings can be attended, otherwise `False`.

## Constraints
- `0 <= len(intervals) <= 10^4`.
- `0 <= start < end <= 10^9`.

## Examples
Input: `intervals = [[0,30],[5,10],[15,20]]`
Output: `False`
Explanation: `[0,30]` overlaps both `[5,10]` and `[15,20]`.

Input: `intervals = [[7,10],[2,4]]`
Output: `True`

Input: `intervals = [[1,5],[5,9],[9,12]]`
Output: `True`
Explanation: Meetings only touch at their endpoints, which is allowed.
