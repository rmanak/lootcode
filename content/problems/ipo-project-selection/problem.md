You can complete at most `k` projects starting with capital `w`. Project `i` needs
`capital[i]` capital up front (which you must already have) and then adds `profits[i]`
to your capital. Capital is never consumed. Return the **maximum capital** after
finishing at most `k` projects.

## Constraints
- `1 <= k <= 10^5`
- `0 <= w <= 10^9`
- `1 <= len(profits) == len(capital) <= 10^5`

## Examples
Input: `k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]`
Output: `4`
Explanation: Take project 0 (capital 0) then project 2.

Input: `k = 1, w = 2, profits = [1,2,3], capital = [1,1,2]`
Output: `5`
Explanation: Take the project with profit 3.
