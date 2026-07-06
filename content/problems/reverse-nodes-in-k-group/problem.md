Given the `head` of a **singly linked list**, reverse the nodes `k` at a time and
return the head of the modified list. If the number of nodes is not a multiple of
`k`, the leftover nodes at the end stay as they are.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

**Examples**
```
head = [1,2,3,4,5], k = 2   ->  [2,1,4,3,5]
head = [1,2,3,4,5], k = 3   ->  [3,2,1,4,5]
```

**Constraints:** `0 <= number of nodes <= 5000`, `1 <= k <= number of nodes` (or `k = 1` when empty).
