Each building is `[left, right, height]` occupying the half-open strip
`[left, right)`. Return **the skyline as a list of key points `[x, height]`**,
sorted by `x`, where each point marks where the outline's height changes. The
final point has height `0` marking the right end of the rightmost building. No two
consecutive points share the same height.

## Constraints
- `0 <= len(buildings) <= 10^4`.
- `0 <= left < right <= 10^9`, `1 <= height <= 10^9`.

## Examples
Input: `buildings = [[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]]`
Output: `[[2,10],[3,15],[7,12],[12,0],[15,10],[20,8],[24,0]]`

Input: `buildings = [[0,2,3],[2,5,3]]`
Output: `[[0,3],[5,0]]`

Input: `buildings = []`
Output: `[]`
