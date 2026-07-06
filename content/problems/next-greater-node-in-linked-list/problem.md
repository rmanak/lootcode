Given the `head` of a **singly linked list**, for each node find the value of the
**first node after it** that is strictly larger; if there is none, use `0`. Return
these values as an array `answer` of the same length as the list (the i-th entry is
the answer for the i-th node).

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the
class is provided). The list is shown below as the array of its node values; the
return value is a plain array of integers.

**Examples**
```
head = [2,1,5]               ->  [5,5,0]
head = [2,7,4,3,5]           ->  [7,0,5,5,0]
head = [1,7,5,1,9,2,5,1]     ->  [7,9,9,9,0,5,0,0]
```

**Constraints:** `0 <= number of nodes <= 10^4`, `1 <= Node.val <= 10^9`.
