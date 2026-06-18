Cars drive toward `target` on a one-lane road; car `i` starts at `position[i]` with
constant `speed[i]` and never passes another car (a faster car catches up and then
travels as one **fleet** at the slower car's speed). Return the **number of fleets**
that arrive at `target`.

## Constraints
- `1 <= len(position) == len(speed) <= 10^5`
- `0 < target <= 10^9`, positions are distinct and less than `target`
- `1 <= speed[i] <= 10^6`

## Examples
Input: `target = 12, position = [10,8,0,5,3], speed = [2,4,1,1,3]`
Output: `3`
Explanation: The cars merge into three fleets before reaching `target`.

Input: `target = 10, position = [3], speed = [3]`
Output: `1`
Explanation: A single car is its own fleet.
