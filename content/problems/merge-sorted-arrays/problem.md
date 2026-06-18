Given two arrays `a` and `b`, each sorted in non-decreasing order, return **one
sorted array** containing all elements of both (a merged multiset).

## Constraints
- `0 <= len(a), len(b) <= 10^5`.
- `a` and `b` are each sorted non-decreasing; `-10^9 <= values <= 10^9`.

## Examples
Input: `a = [1,2,3], b = [2,5,6]`
Output: `[1,2,2,3,5,6]`

Input: `a = [], b = [1]`
Output: `[1]`

Input: `a = [4], b = []`
Output: `[4]`
