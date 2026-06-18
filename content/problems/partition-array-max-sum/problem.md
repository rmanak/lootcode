Partition `arr` into contiguous blocks of length **at most** `k`. After
partitioning, every value in a block becomes the block's maximum. Return the
**largest possible sum** of the resulting array.

## Constraints
- `1 <= len(arr) <= 500`
- `1 <= k <= len(arr)`
- `0 <= arr[i] <= 10^9`

## Examples
Input: `arr = [1,15,7,9,2,5,10], k = 3`
Output: `84`
Explanation: Blocks `[1,15,7] [9] [2,5,10]` → `15*3 + 9 + 10*3 = 84`.

Input: `arr = [1,4,1,5,7,3,6,1,9,9,3], k = 4`
Output: `83`
Explanation: An optimal partition gives `83`.
