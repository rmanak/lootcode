`events` is a list of `[user, time]` pairs sorted by `time`. For each user, group
consecutive events into **sessions**, starting a new session whenever the gap to the
previous event for that user is **strictly greater** than `gap`. Return each session
as `[user, [start_time, end_time]]`, sorted by `start_time`, then `end_time`, then
`user`.

## Constraints
- `0 <= len(events) <= 2*10^5`
- `events` is sorted by `time`; `gap >= 0`

## Examples
Input: `events = [["u",1],["u",3],["u",10]], gap = 5`
Output: `[["u",[1,3]],["u",[10,10]]]`
Explanation: `3 -> 10` exceeds the gap, starting a new session.

Input: `events = [["a",2]], gap = 5`
Output: `[["a",[2,2]]]`
Explanation: A single event is its own session.
