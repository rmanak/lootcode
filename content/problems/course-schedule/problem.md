There are `numCourses` courses labelled `0` to `numCourses - 1`. Each
`prerequisites[i] = [a, b]` means course `b` must be taken before course `a`.
Return **`true` if it is possible to finish every course** — i.e. the
prerequisite graph contains no cycle.

## Constraints
- `1 <= numCourses <= 2000`
- `0 <= len(prerequisites) <= 5000`, `prerequisites[i].length == 2`
- `0 <= a, b < numCourses`; all pairs are distinct

## Examples
Input: `numCourses = 2, prerequisites = [[1,0]]`
Output: `true`

Input: `numCourses = 2, prerequisites = [[1,0],[0,1]]`
Output: `false`
Explanation: courses `0` and `1` each require the other.
