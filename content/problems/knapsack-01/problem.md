Given items with `values[i]` and `weights[i]`, and a knapsack `capacity`, choose a
subset of items (each used at most once) whose total weight does not exceed
`capacity`. Return **the maximum total value** achievable.

## Constraints
- `0 <= len(values) == len(weights) <= 1000`, `0 <= capacity <= 10^4`.
- `0 <= values[i] <= 10^4`, `0 <= weights[i] <= 10^4`.

## Examples
Input: `values = [60,100,120], weights = [10,20,30], capacity = 50`
Output: `220`
Explanation: take items 2 and 3 (weight `50`, value `220`).

Input: `values = [1,2,3], weights = [4,5,6], capacity = 3`
Output: `0`

Input: `values = [10], weights = [5], capacity = 5`
Output: `10`
