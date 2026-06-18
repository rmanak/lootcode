You have `n` jobs; job `i` runs in the half-open interval `[start[i], end[i])` and
pays `profit[i]`. Choose a subset of **non-overlapping** jobs (a job may start exactly
when another ends) to maximize total profit. Return that maximum profit.

## Constraints
- `1 <= len(start) == len(end) == len(profit) <= 5*10^4`
- `0 <= start[i] < end[i] <= 10^9`, `1 <= profit[i] <= 10^4`

## Examples
Input: `start = [1,2,3,3], end = [3,4,5,6], profit = [50,10,40,70]`
Output: `120`
Explanation: Run jobs `[1,3)` and `[3,6)` for `50 + 70`.

Input: `start = [1,1,1], end = [2,3,4], profit = [5,6,4]`
Output: `6`
Explanation: The three jobs all overlap, so take the best single one.
