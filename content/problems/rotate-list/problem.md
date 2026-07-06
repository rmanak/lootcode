> **Format:** the linked list is given, and returned, as an **array of its node values** (`[]` = empty list).

Given the `head` of a linked list, rotate the list to the right by `k` places.

**Example 1:**

![](/problems/rotate-list/assets/rotate1.jpg)

```
Input: head = [1,2,3,4,5], k = 2
Output: [4,5,1,2,3]
```

**Example 2:**

![](/problems/rotate-list/assets/roate2.jpg)

```
Input: head = [0,1,2], k = 4
Output: [2,0,1]
```

**Constraints:**

- The number of nodes in the list is in the range `[0, 500]`.
- `-100 <= Node.val <= 100`
- `0 <= k <= 2 * 10^9`
