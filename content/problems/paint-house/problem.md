There are `n` houses in a row, each painted one of three colors. `costs[i] =
[red, green, blue]` is the cost of each color for house `i`. No two **adjacent**
houses may share a color. Return the **minimum total painting cost**.

## Constraints
- `1 <= len(costs) <= 100`
- `costs[i]` has exactly 3 non-negative values

## Examples
Input: `costs = [[17,2,17],[16,16,5],[14,3,19]]`
Output: `10`
Explanation: Green, blue, green → `2 + 5 + 3 = 10`.

Input: `costs = [[7,6,2]]`
Output: `2`
Explanation: Paint the single house its cheapest color.
