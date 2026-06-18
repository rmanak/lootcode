Replay a sequence of booking `operations`, each `["book", start, end]` for the
half-open interval `[start, end)`. Return **a list of booleans**: `true` if the
interval does **not** overlap any previously booked interval (the booking is then
kept), or `false` if it overlaps (and is discarded).

## Constraints
- `1 <= len(operations) <= 10^4`.
- `0 <= start < end <= 10^9`.

## Examples
Input: `operations = [["book",10,20],["book",15,25],["book",20,30]]`
Output: `[true,false,true]`
Explanation: `[15,25)` overlaps `[10,20)`; `[20,30)` touches but does not overlap.

Input: `operations = [["book",0,5],["book",5,10]]`
Output: `[true,true]`

Input: `operations = [["book",1,4],["book",2,3]]`
Output: `[true,false]`
