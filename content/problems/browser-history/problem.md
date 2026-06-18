Start on `homepage` and replay `operations`, returning the list of results.
Operations are `["visit", url]` (go to `url`, clearing forward history; returns
`null`), `["back", steps]` (move back up to `steps` pages, returning the current
url), and `["forward", steps]` (move forward up to `steps`, returning the current
url). You cannot move past either end.

## Constraints
- `1 <= len(operations) <= 5000`
- urls are non-empty strings; `1 <= steps`

## Examples
Input: `homepage = "a.com", operations = [["visit","b.com"],["visit","c.com"],["back",1],["forward",1]]`
Output: `[null,null,"b.com","c.com"]`
Explanation: Back lands on `b.com`; forward returns to `c.com`.

Input: `homepage = "x.com", operations = [["visit","y.com"],["back",2]]`
Output: `[null,"x.com"]`
Explanation: Back is clamped to the homepage.
