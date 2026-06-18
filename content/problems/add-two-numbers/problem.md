Two non-empty lists `l1` and `l2` store the digits of non-negative integers in
**reverse** order (the ones digit first), one digit per element. Return the digits of
their sum in the same reverse-order list format.

## Constraints
- `1 <= len(l1), len(l2) <= 100`
- each element is a digit `0..9`; no leading zero except the number `0` itself

## Examples
Input: `l1 = [2,4,3], l2 = [5,6,4]`
Output: `[7,0,8]`
Explanation: `342 + 465 = 807`, stored as `[7,0,8]`.

Input: `l1 = [9,9], l2 = [1]`
Output: `[0,0,1]`
Explanation: `99 + 1 = 100`.
