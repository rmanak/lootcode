Replay a sequence of stack `operations` and return **the list of results**. Each
operation is one of `["push", x]`, `["pop"]`, `["top"]`, `["getMin"]`. `push` and
`pop` return `null`; `top` returns the top value; `getMin` returns the current
minimum. All operations run in `O(1)`.

## Constraints
- `1 <= len(operations) <= 10^4`.
- `pop`, `top`, `getMin` are only issued when the stack is non-empty.
- `-10^9 <= x <= 10^9`.

## Examples
Input: `operations = [["push",-2],["push",0],["push",-3],["getMin"],["pop"],["top"],["getMin"]]`
Output: `[null,null,null,-3,null,0,-2]`

Input: `operations = [["push",5],["top"],["getMin"]]`
Output: `[null,5,5]`

Input: `operations = [["push",1],["push",1],["getMin"],["pop"],["getMin"]]`
Output: `[null,null,1,null,1]`
