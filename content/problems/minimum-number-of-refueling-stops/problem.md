A car must drive `target` miles starting with `startFuel` liters (1 liter per
mile). `stations[i] = [position, fuel]` is a station `position` miles from the
start holding `fuel` liters; stopping there adds all its fuel. **Return the minimum
number of stops** to reach `target`, or `-1` if impossible.

**Examples**
```
target = 1,   startFuel = 1,  stations = []                            ->  0
target = 100, startFuel = 1,  stations = [[10,100]]                    ->  -1
target = 100, startFuel = 10, stations = [[10,60],[20,30],[30,30],[60,40]] ->  2
```

**Constraints:** `1 <= target, startFuel, stations[i][1] <= 10^9`,
`0 <= len(stations) <= 500`, station positions strictly increasing and `< target`.
