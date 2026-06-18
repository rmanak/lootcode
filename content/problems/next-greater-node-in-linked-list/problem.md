A singly linked list is given as an array of values `head` (the i-th value is the
i-th node). For each node, find the value of the **first node after it** that is
strictly larger; if there is none, use `0`. Return these values as an array `answer`
of the same length as `head`.

**Examples**
```
head = [2,1,5]               ->  [5,5,0]
head = [2,7,4,3,5]           ->  [7,0,5,5,0]
head = [1,7,5,1,9,2,5,1]     ->  [7,9,9,9,0,5,0,0]
```

**Constraints:** `0 <= len(head) <= 10^4`, `1 <= head[i] <= 10^9`.
