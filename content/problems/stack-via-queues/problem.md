Implement a LIFO stack using queues and replay `operations`, returning the list of
results. Operations are `["push", x]` (returns `null`), `["pop"]` (removes and
returns the top), `["top"]` (returns the top), and `["empty"]` (returns a boolean).

## Constraints
- `1 <= len(operations) <= 1000`
- `pop`/`top` are only called on a non-empty stack

## Examples
Input: `operations = [["push",1],["push",2],["top"],["pop"],["empty"]]`
Output: `[null,null,2,2,false]`
Explanation: The most recently pushed value leaves first.

Input: `operations = [["push",7],["pop"],["empty"]]`
Output: `[null,7,true]`
Explanation: After popping the only value, the stack is empty.
