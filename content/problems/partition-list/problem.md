Given the `head` of a **singly linked list** and a value `x`, partition it so that
all nodes **less than** `x` come before nodes **greater than or equal to** `x`.

You should **preserve** the original relative order of the nodes in each of the two
partitions. Return the head of the partitioned list.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

**Example 1:**

![](/problems/partition-list/assets/partition.jpg)

```
Input: head = [1,4,3,2,5,2], x = 3
Output: [1,2,2,4,3,5]
```

**Example 2:**

```
Input: head = [2,1], x = 2
Output: [1,2]
```

**Constraints:**

- The number of nodes in the list is in the range `[0, 200]`.
- `-100 <= Node.val <= 100`
- `-200 <= x <= 200`
