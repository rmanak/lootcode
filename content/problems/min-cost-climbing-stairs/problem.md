`cost[i]` is the price to step on stair `i`. You may start at index `0` or `1`, and
from a stair you climb one or two steps. Return the **minimum total cost** to reach
the top (just past the last stair).

## Constraints
- `2 <= len(cost) <= 1000`
- `0 <= cost[i] <= 999`

## Examples
Input: `cost = [10,15,20]`
Output: `15`
Explanation: Start on stair 1 (cost 15) and step to the top.

Input: `cost = [1,100,1,1,1,100,1,1,100,1]`
Output: `6`
Explanation: Step on the six stairs that cost `1`.
