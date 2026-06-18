A singly linked list is given as an array of values `head`. Reverse the nodes `k` at
a time and return the resulting list of values. If the number of nodes is not a
multiple of `k`, the leftover nodes at the end stay as they are.

**Examples**
```
head = [1,2,3,4,5], k = 2   ->  [2,1,4,3,5]
head = [1,2,3,4,5], k = 3   ->  [3,2,1,4,5]
```

**Constraints:** `0 <= len(head) <= 5000`, `1 <= k <= len(head)` (or `k = 1` when empty).
