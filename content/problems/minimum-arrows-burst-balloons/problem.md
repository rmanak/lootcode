Each balloon spans the inclusive horizontal interval `points[i] = [start, end]`. An
arrow shot straight up at coordinate `x` bursts every balloon with `start <= x <=
end`. Return the **minimum number of arrows** needed to burst all balloons.

## Constraints
- `1 <= len(points) <= 10^5`
- `points[i] = [start, end]` with `start <= end`

## Examples
Input: `points = [[10,16],[2,8],[1,6],[7,12]]`
Output: `2`
Explanation: One arrow in `[2,6]` and one in `[10,12]`.

Input: `points = [[1,2],[3,4],[5,6]]`
Output: `3`
Explanation: No balloons overlap, so each needs its own arrow.
