Given a linked list as an array `head`, reverse its nodes `k` at a time and return
the resulting list. Nodes left over (fewer than `k`) at the end keep their original
order.

## Constraints
- `0 <= len(head) <= 5000`
- `1 <= k <= len(head)` (or `k` may exceed a short list, leaving it unchanged)

## Examples
Input: `head = [1,2,3,4,5], k = 2`
Output: `[2,1,4,3,5]`
Explanation: Reverse each consecutive pair; the trailing `5` stays.

Input: `head = [1,2,3,4,5], k = 3`
Output: `[3,2,1,4,5]`
Explanation: Only the first full group of three is reversed.
