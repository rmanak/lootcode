Replay `operations` against a time-keyed store and return the list of results. Each
operation is `["set", key, value, timestamp]` (returns `null`) or
`["get", key, timestamp]`, which returns the value of `key` set at the **largest**
timestamp `<= timestamp`, or `""` if none exists. `set` timestamps for a key are
strictly increasing.

## Constraints
- `1 <= len(operations) <= 2*10^5`
- keys and values are non-empty strings; `1 <= timestamp <= 10^7`

## Examples
Input: `operations = [["set","foo","bar",1],["get","foo",1],["get","foo",3]]`
Output: `[null,"bar","bar"]`
Explanation: The value set at timestamp 1 is still current at timestamp 3.

Input: `operations = [["set","a","x",5],["get","a",4]]`
Output: `[null,""]`
Explanation: There is no value at or before timestamp 4.
