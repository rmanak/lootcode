`cost[i]` is the cost of deleting `s[i]`. **Return the minimum total cost to delete
characters so that no two equal letters are adjacent.**

**Examples**
```
s = "abaac", cost = [1,2,3,4,5]  ->  3
s = "abc", cost = [1,2,3]        ->  0
s = "aabaa", cost = [1,2,3,4,1]  ->  2
```

**Constraints:** `1 <= len(s) == len(cost) <= 10^5`, `1 <= cost[i] <= 10^4`,
lowercase letters.
