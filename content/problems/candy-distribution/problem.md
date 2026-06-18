Each child stands in a line with an integer rating. Distribute candies so that
every child gets at least one candy and any child with a strictly higher rating
than an adjacent neighbor gets strictly more candies than that neighbor. Return
**the minimum total number of candies** required.

## Constraints
- `1 <= len(ratings) <= 2*10^4`.
- `0 <= ratings[i] <= 10^9`.

## Examples
Input: `ratings = [1,0,2]`
Output: `5`
Explanation: candies `[2,1,2]`.

Input: `ratings = [1,2,2]`
Output: `4`
Explanation: candies `[1,2,1]`.

Input: `ratings = [1,3,2,2,1]`
Output: `7`
