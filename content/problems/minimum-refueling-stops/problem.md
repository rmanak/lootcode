A car starts with `startFuel` liters and burns one liter per unit distance toward
`target`. Each `stations[i] = [position, fuel]` (sorted by position) can add `fuel`
liters when reached. Return the **minimum number of refueling stops** to reach
`target`, or `-1` if it is impossible.

## Constraints
- `1 <= target, startFuel <= 10^9`
- `0 <= len(stations) <= 500`
- stations are sorted by increasing `position`, all `< target`

## Examples
Input: `target = 100, startFuel = 10, stations = [[10,60],[20,30],[30,30],[60,40]]`
Output: `2`
Explanation: Refuel at positions 10 and 60.

Input: `target = 1, startFuel = 1, stations = []`
Output: `0`
Explanation: The starting fuel already reaches the target.
