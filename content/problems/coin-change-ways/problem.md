Given an integer `amount` and a list of distinct positive coin denominations
`coins` (unlimited supply of each), return **the number of distinct combinations
of coins that sum to `amount`**. Combinations are unordered, so `1+2` and `2+1`
count once.

## Constraints
- `0 <= amount <= 5000`, `1 <= len(coins) <= 300`.
- `1 <= coins[i] <= 5000`, all distinct.

## Examples
Input: `amount = 5, coins = [1,2,5]`
Output: `4`
Explanation: `5`, `2+2+1`, `2+1+1+1`, `1+1+1+1+1`.

Input: `amount = 3, coins = [2]`
Output: `0`

Input: `amount = 0, coins = [7]`
Output: `1`
Explanation: the empty combination.
