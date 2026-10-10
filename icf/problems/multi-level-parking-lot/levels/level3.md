The lot now accepts buses. A bus is too long for a single spot, so it takes a
row of regular spots next to each other. Staff also need to see what is parked
on a level, so implement an operation that lists the vehicles on it.

### How the existing operations change

`park` now also accepts `vehicle_type` `"bus"`:

- A **bus** needs **5 consecutive free regular (`'R'`) spots on the same
  level**, and it takes all five. A motorcycle spot or an occupied spot breaks
  the row, and a row never continues from one level onto the next.
- The bus takes the first such row: on the first level (in the order levels
  were added) that has one, the leftmost row of 5.
- The bus's spot is the **leftmost** of its five spots. That is what `park`
  returns, and what `find_vehicle` and `unpark` return for the bus.
- `park` returns `None`, and parks nothing, if no level has 5 consecutive free
  regular spots, or if a vehicle with this plate is already parked.
- `unpark` frees all five spots at once.
- `count_free` and `top_levels` count each of the five spots, so a parked bus
  lowers its level's count of free regular spots by 5.

Motorcycles and cars follow exactly the same rules as before. A car may take
a spot that leaves no room for a bus.

```python
list_level(self, timestamp: int, level_id: str) -> list[str] | None
```

should return the plates of the vehicles parked on the level `level_id`,
ordered by the position of their spot from left to right. A bus appears once,
at the position of its leftmost spot. Returns an empty list if nothing is
parked on the level, or `None` if the level doesn't exist.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `lot = ParkingLot()` | a new lot with no levels |
| `lot.add_level(1, "G", "RRRMRRRRRR")` | returns `True`; regular spots 0–2 and 4–9, a motorcycle spot at 3 |
| `lot.add_level(2, "P1", "RRRRR")` | returns `True` |
| `lot.park(3, "C-1", "car")` | returns `"G-0"` |
| `lot.park(4, "BUS-1", "bus")` | returns `"G-4"`; spots 1–2 are only two in a row before the motorcycle spot, so the bus takes spots 4–8 |
| `lot.park(5, "BUS-2", "bus")` | returns `"P1-0"`; level `"G"` has only spot 9 left after spot 8, so the bus goes to `"P1"` |
| `lot.park(6, "BUS-3", "bus")` | returns `None`; no level has 5 free regular spots in a row |
| `lot.list_level(7, "G")` | returns `["C-1", "BUS-1"]` |
| `lot.count_free(8, "G", "R")` | returns `3`; spots 1, 2 and 9 |
| `lot.find_vehicle(9, "BUS-1")` | returns `"G-4"` |
| `lot.unpark(10, "C-1")` | returns `"G-0"` |
| `lot.park(11, "M-1", "motorcycle")` | returns `"G-3"` |
| `lot.list_level(12, "G")` | returns `["M-1", "BUS-1"]`; ordered by spot position, not by arrival |
| `lot.unpark(13, "BUS-1")` | returns `"G-4"`; spots 4–8 are all free again |
| `lot.list_level(14, "G")` | returns `["M-1"]` |
| `lot.list_level(15, "P9")` | returns `None`; there is no level `"P9"` |
