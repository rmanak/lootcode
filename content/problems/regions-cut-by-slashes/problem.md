`grid` is an `n x n` board of characters `'/'`, `'\\'`, and `' '` (space). Each cell
is a unit square that a slash divides into regions. Return the **number of contiguous
regions** the whole board is divided into.

## Constraints
- `1 <= n <= 30`
- each row is a string of length `n` over `'/'`, `'\\'`, `' '`

## Examples
Input: `grid = [" /","/ "]`
Output: `2`
Explanation: The two slashes split the square into two regions.

Input: `grid = [" /","  "]`
Output: `1`
Explanation: A single slash does not fully enclose a separate region.
