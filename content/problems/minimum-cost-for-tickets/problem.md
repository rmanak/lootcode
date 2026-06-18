You planned train trips on the given `days` of the year (each `1..365`). Tickets:
a 1-day pass for `costs[0]`, a 7-day pass for `costs[1]`, a 30-day pass for
`costs[2]`. A pass bought on day `d` covers that many **consecutive** days from
`d`. **Return the minimum cost** to cover every travel day.

**Examples**
```
days = [1,4,6,7,8,20], costs = [2,7,15]                  ->  11
days = [1,2,3,4,5,6,7,8,9,10,30,31], costs = [2,7,15]    ->  17
```

**Constraints:** `1 <= len(days) <= 365`, `1 <= days[i] <= 365` strictly
increasing, `len(costs) == 3`, `1 <= costs[i] <= 1000`.
