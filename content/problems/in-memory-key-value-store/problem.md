Replay `operations` against a versioned key-value store and return **the list of
results**. Operations are: `["set", key, value]` → `null`; `["get", key]` → the
current value or `null` if absent; `["delete", key]` → `null`; `["snapshot"]` →
returns a new version id (`0, 1, 2, ...`) capturing the current contents;
`["getAt", key, id]` → the value of `key` in snapshot `id` (or `null` if absent or
`id` is invalid).

## Constraints
- `1 <= len(operations) <= 10^5`.
- Snapshot ids are assigned in increasing order starting from `0`.

## Examples
Input: `operations = [["set","a",1],["snapshot"],["set","a",2],["get","a"],["getAt","a",0],["delete","a"],["get","a"]]`
Output: `[null,0,null,2,1,null,null]`

Input: `operations = [["get","x"]]`
Output: `[null]`

Input: `operations = [["set","k",9],["snapshot"],["delete","k"],["getAt","k",0]]`
Output: `[null,0,null,9]`
