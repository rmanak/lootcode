A sliding-window rate limiter allows at most `limit` requests per user within any
`window` seconds. Replay `operations`, each `["request", userId, timestamp]`, and
return **a list of booleans**: `true` if the request is allowed (fewer than
`limit` of that user's *allowed* requests fall in `(timestamp-window, timestamp]`)
and is then recorded, or `false` if it is rejected. Timestamps are non-decreasing.

## Constraints
- `1 <= limit <= 10^4`, `1 <= window <= 10^9`, `1 <= len(operations) <= 10^5`.
- Timestamps are non-decreasing.

## Examples
Input: `limit = 2, window = 10, operations = [["request","a",1],["request","a",2],["request","a",3],["request","a",11]]`
Output: `[true,true,false,true]`

Input: `limit = 1, window = 5, operations = [["request","a",1],["request","b",1],["request","a",2]]`
Output: `[true,true,false]`

Input: `limit = 3, window = 100, operations = [["request","x",50]]`
Output: `[true]`
