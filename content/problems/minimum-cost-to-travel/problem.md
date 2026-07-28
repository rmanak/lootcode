# Minimum Cost to Travel

A car must drive from point `A` to point `B`, which are `target` units apart.
Its fuel tank holds at most `capacity` units and **starts completely full**.
Driving consumes exactly **1 unit of fuel per unit of distance**.

There are `m` gas stations along the way. Station `i` sits `position[i]` units
past `A` and sells fuel at `price[i]` per unit. Every station has an unlimited
supply, so at each one you may buy any non-negative integer amount of fuel — as
long as the tank never holds more than `capacity` units. You may also drive past
a station without buying anything, and fuel already in the tank is never lost.

Return the **minimum total cost** to travel from `A` to `B`, or `-1` if the trip
is impossible.

## Constraints

- `1 <= m <= 10^5`
- `position.length == price.length == m`
- `0 < position[0] < position[1] < ... < position[m-1] < target <= 10^9`
- `1 <= price[i] <= 10^9`
- `1 <= capacity <= 10^9`
- `position` is strictly increasing.

## Examples

**Example 1**
```
Input:  target = 20, capacity = 8, position = [3, 7, 12, 16], price = [9, 2, 6, 4]
Output: 36
Explanation:
  Leave A with a full tank of 8 and reach station 0 (position 3) holding 5.
  Its fuel costs 9 -- the priciest on the route -- and the cheap station 1 is
  only 4 units further, well within range, so buy nothing.
  Arrive at station 1 (position 7) with 1 unit. At 2 per unit this is the
  cheapest fuel left, so fill the tank completely: 7 units * 2 = 14.
  Arrive at station 2 (position 12) with 3 units. It costs 6, but station 3 is
  cheaper at 4 and sits 4 units away, so buy only enough to get there:
  1 unit * 6 = 6.
  Arrive at station 3 (position 16) empty with 4 units left to travel, and
  nothing cheaper remains: 4 units * 4 = 16.
  Total = 14 + 6 + 16 = 36.
```

**Example 2**
```
Input:  target = 4, capacity = 6, position = [2], price = [7]
Output: 0
Explanation: The starting tank of 6 units already covers the whole distance of
4, so the car drives straight to B without stopping.
```

**Example 3**
```
Input:  target = 12, capacity = 5, position = [2, 9], price = [4, 4]
Output: -1
Explanation: Even filling up completely at station 0 (position 2) strands the
car at position 7, short of station 1 at position 9. That gap is wider than one
tank, so B cannot be reached.
```

> Distances are expressed directly in fuel units. A variant that gives real
> distances plus a consumption rate is the same problem — divide through by the
> rate first.
