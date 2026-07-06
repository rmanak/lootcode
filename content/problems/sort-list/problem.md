Given the `head` of a **singly linked list**, return the head of the list after
sorting its nodes in **ascending order**.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

**Example 1:**

![](/problems/sort-list/assets/sort_list_1.jpg)

```
Input: head = [4,2,1,3]
Output: [1,2,3,4]
```

**Example 2:**

![](/problems/sort-list/assets/sort_list_2.jpg)

```
Input: head = [-1,5,3,4,0]
Output: [-1,0,3,4,5]
```

**Example 3:**

```
Input: head = []
Output: []
```

**Constraints:**

- The number of nodes in the list is in the range `[0, 5 * 10^4]`.
- `-10^5 <= Node.val <= 10^5`

**Follow up:** Can you sort the linked list in `O(n logn)` time and `O(1)` memory (i.e. constant space)?
