There are `numCourses` courses labelled `0..numCourses-1`. Each pair `[a, b]` in
`prerequisites` means course `b` must be taken before course `a`. Return **a valid
ordering of all courses**; if several exist, return the **lexicographically
smallest** one. Return `[]` if no ordering exists.

## Constraints
- `1 <= numCourses <= 2000`, `0 <= len(prerequisites) <= 5000`.
- `prerequisites[i] = [a, b]` with `0 <= a, b < numCourses`.

## Examples
Input: `numCourses = 2, prerequisites = [[1,0]]`
Output: `[0,1]`

Input: `numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]`
Output: `[0,1,2,3]`

Input: `numCourses = 2, prerequisites = [[0,1],[1,0]]`
Output: `[]`
Explanation: the two courses depend on each other.
