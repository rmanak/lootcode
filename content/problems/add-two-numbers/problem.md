You are given two **non-empty singly linked lists** `l1` and `l2` representing two
non-negative integers. The digits are stored in **reverse** order (the ones digit
first), one digit per node. Add the two numbers and return the sum as a linked list
in the same reverse-order form.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

**Constraints**
- `1 <= number of nodes in each list <= 100`
- each node's value is a digit `0..9`; the number has no leading zero except `0` itself

**Examples**
Input: `l1 = [2,4,3], l2 = [5,6,4]`
Output: `[7,0,8]`
Explanation: `342 + 465 = 807`, stored as `[7,0,8]`.

Input: `l1 = [9,9], l2 = [1]`
Output: `[0,0,1]`
Explanation: `99 + 1 = 100`.
