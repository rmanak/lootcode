Given an array `arr` and a list of `queries` where each query is `[l, r]` (an
inclusive index range), return **for each query the length of the longest run of
equal consecutive values within `arr[l..r]`**.

## Constraints
- `1 <= len(arr) <= 2000`, `1 <= len(queries) <= 2000`.
- `0 <= l <= r < len(arr)`.

## Examples
Input: `arr = [1,1,2,2,2,3], queries = [[0,2],[1,4],[0,5]]`
Output: `[2,3,3]`

Input: `arr = [5], queries = [[0,0]]`
Output: `[1]`

Input: `arr = [7,7,7,7], queries = [[1,3]]`
Output: `[3]`
