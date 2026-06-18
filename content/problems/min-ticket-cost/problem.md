You travel on the given `days` (a sorted list within a year, `1..365`). Passes cost
`costs = [oneDay, sevenDay, thirtyDay]` and cover 1, 7, or 30 **consecutive** days
from their purchase. Return the **minimum cost** to cover all travel days.

## Constraints
- `1 <= len(days) <= 365`, days are strictly increasing in `1..365`
- `len(costs) == 3`, `1 <= costs[i] <= 1000`

## Examples
Input: `days = [1,4,6,7,8,20], costs = [2,7,15]`
Output: `11`
Explanation: A 7-day pass on day 1 and another on day 7, plus a 1-day pass for day 20.

Input: `days = [1,2,3,4,5,6,7,8,9,10,30,31], costs = [2,7,15]`
Output: `17`
Explanation: A 30-day pass covers days 1–10, plus a 7-day pass for days 30–31.
