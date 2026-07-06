Given the `head` of a **singly linked list**, swap every two adjacent nodes and
return the head of the resulting list. If the list has an odd length, the last node
stays in place. Swap the nodes themselves rather than just their `.val` fields.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

**Example**
```
head = [1,2,3,4]   ->  [2,1,4,3]
```

**Constraints:** `0 <= number of nodes <= 1000`.
