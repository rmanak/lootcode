A singly linked list is given as the value array `head`, plus an integer `pos`:
if `pos >= 0`, the last node's `next` points back to the node at index `pos`,
forming a cycle; if `pos == -1` the list has no cycle. Return **`true` if the list
contains a cycle**. Use `O(1)` extra space.

## Constraints
- `0 <= len(head) <= 10^4`, `-1 <= pos < len(head)`.

## Examples
Input: `head = [3,2,0,-4], pos = 1`
Output: `true`
Explanation: the tail connects back to the node with value `2`.

Input: `head = [1,2], pos = 0`
Output: `true`

Input: `head = [1], pos = -1`
Output: `false`
