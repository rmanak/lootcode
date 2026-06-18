`events` is a list of `[key, time]` notifications in time order. A notification is
**delivered** only if the same `key` has not been delivered within the previous
`window` seconds (i.e. the gap to the last delivered time for that key is strictly
greater than `window`). Return the delivered notifications, in order.

## Constraints
- `0 <= len(events) <= 2*10^5`, processed in the given order
- `window >= 0`

## Examples
Input: `events = [["a",1],["a",3],["a",8]], window = 5`
Output: `[["a",1],["a",8]]`
Explanation: The event at `3` is within 5s of the delivered event at `1`, so it is
suppressed; `8` is 7s later and delivered.

Input: `events = [["x",1],["y",2]], window = 5`
Output: `[["x",1],["y",2]]`
Explanation: Different keys never suppress each other.
