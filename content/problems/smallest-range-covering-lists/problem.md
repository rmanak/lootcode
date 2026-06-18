Given `k` sorted integer lists, find **the smallest range `[l, r]`** that includes
at least one number from each list. A range `[a, b]` is smaller than `[c, d]` if
`b - a < d - c`, or `b - a == d - c` and `a < c`. Return the range as `[l, r]`.

## Constraints
- `1 <= k <= 3000`; each list is non-empty and sorted ascending.
- `-10^5 <= values <= 10^5`.

## Examples
Input: `lists = [[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]`
Output: `[20,24]`

Input: `lists = [[1,2,3],[1,2,3],[1,2,3]]`
Output: `[1,1]`

Input: `lists = [[5]]`
Output: `[5,5]`
