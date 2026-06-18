A simplified consistent-hash ring places integer server ids on a ring at their own
value. Replay `operations` and return **the list of results**. Operations are
`["addServer", id]` → `null`; `["removeServer", id]` → `null`; `["getServer", key]`
→ the id of the first server **clockwise** from `key`, i.e. the smallest server id
`>= key`, wrapping to the smallest id if none qualifies. If there are no servers,
return `null`.

## Constraints
- `1 <= len(operations) <= 10^5`.
- `0 <= id, key <= 10^9`; adding an existing id or removing an absent id is a no-op.

## Examples
Input: `operations = [["addServer",10],["addServer",20],["addServer",30],["getServer",5],["getServer",15],["getServer",25],["getServer",35],["removeServer",20],["getServer",15]]`
Output: `[null,null,null,10,20,30,10,null,30]`

Input: `operations = [["getServer",1]]`
Output: `[null]`

Input: `operations = [["addServer",7],["getServer",7]]`
Output: `[null,7]`
