The `i`-th person weighs `people[i]`. Each boat holds at most two people and at
most `limit` total weight. **Return the minimum number of boats** needed to carry
everyone (every person fits in some boat).

**Examples**
```
people = [1,2], limit = 3        ->  1
people = [3,2,2,1], limit = 3    ->  3
people = [3,5,3,4], limit = 5    ->  4
```

**Constraints:** `1 <= len(people) <= 5*10^4`, `1 <= people[i] <= limit <= 3*10^4`.
