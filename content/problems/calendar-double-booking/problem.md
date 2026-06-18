Implement a calendar that allows double-booking but never **triple**-booking. Replay
`operations`, each `["book", start, end]` for the half-open interval `[start, end)`.
Return `true` if the event can be added without causing any point to be covered by
three events (and add it), otherwise `false`.

## Constraints
- `1 <= len(operations) <= 1000`
- `0 <= start < end <= 10^9`

## Examples
Input: `operations = [["book",10,20],["book",50,60],["book",10,40],["book",5,15],["book",5,10]]`
Output: `[true,true,true,false,true]`
Explanation: `[5,15)` would triple-book `[10,15)`, so it is rejected.

Input: `operations = [["book",1,5],["book",2,6],["book",6,8]]`
Output: `[true,true,true]`
Explanation: No point is covered three times.
