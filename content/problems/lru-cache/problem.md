Implement a Least-Recently-Used cache of the given `capacity` by replaying
`operations` and returning **the list of results**. Each operation is
`["put", key, value]` (returns `null`) or `["get", key]` (returns the value, or
`-1` if absent). A `get` or `put` counts as a use; when the cache is full a `put`
of a new key evicts the least recently used key. All operations run in `O(1)`
average time.

## Constraints
- `1 <= capacity <= 3000`, `1 <= len(operations) <= 10^4`.
- `0 <= key, value <= 10^9`.

## Examples
Input: `capacity = 2, operations = [["put",1,1],["put",2,2],["get",1],["put",3,3],["get",2],["put",4,4],["get",1],["get",3],["get",4]]`
Output: `[null,null,1,null,-1,null,-1,3,4]`

Input: `capacity = 1, operations = [["put",1,1],["put",2,2],["get",1],["get",2]]`
Output: `[null,null,-1,2]`

Input: `capacity = 2, operations = [["get",1]]`
Output: `[-1]`
