Implement a FIFO queue and replay `operations`, returning the list of results.
Operations are `["push", x]` (returns `null`), `["pop"]` (removes and returns the
front), `["peek"]` (returns the front), and `["empty"]` (returns a boolean).

## Constraints
- `1 <= len(operations) <= 1000`
- `pop`/`peek` are only called on a non-empty queue

## Examples
Input: `operations = [["push",1],["push",2],["peek"],["pop"],["empty"]]`
Output: `[null,null,1,1,false]`
Explanation: Elements leave in insertion order.

Input: `operations = [["empty"]]`
Output: `[true]`
Explanation: A fresh queue is empty.
