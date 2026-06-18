Implement a Least-Frequently-Used cache of the given `capacity` by replaying
`operations` and returning **the list of results**. Operations are
`["put", key, value]` (returns `null`) and `["get", key]` (returns the value or
`-1`). Each `get` or successful `put` increments a key's use count. When full, a
`put` of a new key evicts the key with the smallest use count, breaking ties by
**least recently used**.

## Constraints
- `0 <= capacity <= 10^4`, `1 <= len(operations) <= 10^4`.
- `0 <= key, value <= 10^9`.

## Examples
Input: `capacity = 2, operations = [["put",1,1],["put",2,2],["get",1],["put",3,3],["get",2],["get",3],["put",4,4],["get",1],["get",3],["get",4]]`
Output: `[null,null,1,null,-1,3,null,-1,3,4]`

Input: `capacity = 0, operations = [["put",0,0],["get",0]]`
Output: `[null,-1]`

Input: `capacity = 2, operations = [["put",1,1],["get",1],["get",1]]`
Output: `[null,1,1]`
