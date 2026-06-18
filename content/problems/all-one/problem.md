Implement a structure of string keys with positive counts. Replay `operations`,
returning the list of results. Operations are `["inc", key]` (increment, inserting at
1 if absent; returns `null`), `["dec", key]` (decrement, removing at 0; returns
`null`), `["getMaxKey"]`, and `["getMinKey"]`. The getters return a key with the
largest/smallest count (the **lexicographically smallest** such key to break ties),
or `""` if empty.

## Constraints
- `1 <= len(operations) <= 5*10^4`
- `dec` is only called on a key with a positive count

## Examples
Input: `operations = [["inc","a"],["inc","b"],["inc","a"],["getMaxKey"],["getMinKey"]]`
Output: `[null,null,null,"a","b"]`
Explanation: `a` has count 2, `b` has count 1.

Input: `operations = [["inc","x"],["dec","x"],["getMaxKey"]]`
Output: `[null,null,""]`
Explanation: `x` is removed, leaving the structure empty.
