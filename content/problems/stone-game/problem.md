`piles[i]` stones sit in a row. Two players alternate, each taking a whole pile from
**either end**; both play optimally to maximize their own stone count. Return `true`
if the **first** player ends with strictly more stones than the second.

## Constraints
- `1 <= len(piles) <= 500`
- `1 <= piles[i] <= 10^4`

## Examples
Input: `piles = [5,3,4,5]`
Output: `true`
Explanation: The first player can guarantee more than half the stones.

Input: `piles = [3,7,2,3]`
Output: `true`
Explanation: Optimal play wins for the first player.
