Given `points` on the plane (each `[x, y]`) and an integer `k`, return **the `k`
points closest to the origin** by Euclidean distance. The answer may be returned
**in any order**. Every point has a distinct distance from the origin, so the set
of `k` closest points is unique.

## Constraints
- `1 <= k <= len(points) <= 10^4`.
- `-10^4 <= x, y <= 10^4`; all squared distances `x^2 + y^2` are distinct.

## Examples
Input: `points = [[1,3],[-2,2]], k = 1`
Output: `[[-2,2]]`
Explanation: `(-2)^2 + 2^2 = 8 < 1^2 + 3^2 = 10`.

Input: `points = [[3,3],[5,-1],[-2,4]], k = 2`
Output: `[[3,3],[-2,4]]`

Input: `points = [[0,1]], k = 1`
Output: `[[0,1]]`
