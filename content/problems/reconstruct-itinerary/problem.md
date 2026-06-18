You have a list of airline `tickets = [from, to]`. Among all itineraries that start
at `"JFK"` and use **all** tickets exactly once, return the one that is
**lexicographically smallest** when read as a single list (so the answer is unique).
A valid itinerary is guaranteed to exist.

## Constraints
- `1 <= len(tickets) <= 300`
- airport codes are uppercase 3-letter strings

## Examples
Input: `tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]`
Output: `["JFK","MUC","LHR","SFO","SJC"]`
Explanation: The only itinerary using all tickets.

Input: `tickets = [["JFK","KUL"],["JFK","NRT"],["NRT","JFK"]]`
Output: `["JFK","NRT","JFK","KUL"]`
Explanation: Choosing `KUL` first would strand the `NRT` ticket.
