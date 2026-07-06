Given the `head` of a **sorted singly linked list**, delete **every** node that has
a duplicate value, leaving only nodes whose value appears exactly once. Return the
head of the resulting (still sorted) list.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

**Examples**
```
head = [1,2,3,3,4,4,5]   ->  [1,2,5]
head = [1,1,1,2,3]       ->  [2,3]
```

**Constraints:** `0 <= number of nodes <= 300`; values are sorted in non-decreasing order.
