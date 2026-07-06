Given the `head` of a **singly linked list**, reverse the nodes of the list `k` at a
time and return the head of the modified list. Nodes left over (fewer than `k`) at
the end keep their original order.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

## Constraints
- `0 <= number of nodes <= 5000`
- `1 <= k <= number of nodes` (or `k` may exceed a short list, leaving it unchanged)

## Examples
Input: `head = [1,2,3,4,5], k = 2`
Output: `[2,1,4,3,5]`
Explanation: Reverse each consecutive pair; the trailing `5` stays.

Input: `head = [1,2,3,4,5], k = 3`
Output: `[3,2,1,4,5]`
Explanation: Only the first full group of three is reversed.
