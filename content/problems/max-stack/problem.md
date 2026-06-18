Implement a stack that also supports retrieving and removing the maximum. Replay
`operations`, returning the list of results. Operations are `["push", x]` (returns
`null`), `["pop"]` (remove and return the top), `["top"]` (return the top),
`["peekMax"]` (return the maximum), and `["popMax"]` (remove and return the maximum;
if it appears multiple times, remove the one closest to the top).

## Constraints
- `1 <= len(operations) <= 10^4`
- `pop`/`top`/`peekMax`/`popMax` are only called on a non-empty stack

## Examples
Input: `operations = [["push",5],["push",1],["push",5],["top"],["popMax"],["top"]]`
Output: `[null,null,null,5,5,1]`
Explanation: `popMax` removes the most recent `5`, leaving `1` on top.

Input: `operations = [["push",2],["peekMax"]]`
Output: `[null,2]`
Explanation: The only value is the maximum.
