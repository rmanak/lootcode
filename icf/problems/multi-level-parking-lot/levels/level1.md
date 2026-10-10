Initially, the parking lot has no levels at all, so implement operations to
add levels, to park motorcycles and cars, to let them leave, and to find where
a vehicle is. This is the core of the system — every later level builds on
where each vehicle is parked.

```python
add_level(self, timestamp: int, level_id: str, layout: str) -> bool
```

should add a new level with the given identifier and layout (see the data
model in the overview). The new level is searched after every level that
already exists. Returns `True` if the level was added, or `False` if a level
with `level_id` already exists — in which case the existing level is left
exactly as it was.

```python
park(self, timestamp: int, plate: str, vehicle_type: str) -> str | None
```

should park the vehicle with licence plate `plate` and return the identifier of
the spot it was given. `vehicle_type` is `"motorcycle"` or `"car"`, and the two
follow different rules:

- A **motorcycle** takes the first free motorcycle (`'M'`) spot in the whole
  lot. Only if no motorcycle spot is free on any level does it take the first
  free regular (`'R'`) spot.
- A **car** takes the first free regular (`'R'`) spot. A car never uses a
  motorcycle spot.

Returns `None`, and parks nothing, if:

- a vehicle with this plate is already parked, or
- there is no free spot the vehicle is allowed to use.

```python
unpark(self, timestamp: int, plate: str) -> str | None
```

should remove the vehicle with licence plate `plate` from the lot, which frees
its spot. Returns the identifier of the spot the vehicle was in, or `None` if
no vehicle with this plate is parked. A vehicle that has left may park again
later, and it gets a spot by the same rules as any other arrival.

```python
find_vehicle(self, timestamp: int, plate: str) -> str | None
```

should return the identifier of the spot where the vehicle with licence plate
`plate` is parked, or `None` if no vehicle with this plate is parked.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `lot = ParkingLot()` | a new lot with no levels |
| `lot.park(1, "KX-512", "car")` | returns `None`; there are no levels yet |
| `lot.add_level(2, "G", "MRR")` | returns `True`; spots `"G-0"` (M), `"G-1"` (R), `"G-2"` (R) |
| `lot.add_level(3, "G", "RRRR")` | returns `False`; the level `"G"` already exists and keeps its layout |
| `lot.add_level(4, "P1", "RM")` | returns `True`; spots `"P1-0"` (R), `"P1-1"` (M) |
| `lot.park(5, "M-1", "motorcycle")` | returns `"G-0"`, the first motorcycle spot |
| `lot.park(6, "C-1", "car")` | returns `"G-1"`, the first regular spot |
| `lot.park(7, "M-2", "motorcycle")` | returns `"P1-1"`; a motorcycle spot on the next level comes before any regular spot |
| `lot.park(8, "M-3", "motorcycle")` | returns `"G-2"`; no motorcycle spot is free, so it takes the first free regular spot |
| `lot.park(9, "C-2", "car")` | returns `"P1-0"` |
| `lot.park(10, "C-3", "car")` | returns `None`; every regular spot is taken |
| `lot.park(11, "M-3", "car")` | returns `None`; a vehicle with the plate `"M-3"` is already parked |
| `lot.unpark(12, "M-1")` | returns `"G-0"`; the motorcycle spot is free again |
| `lot.park(13, "C-3", "car")` | returns `None`; a car cannot use the motorcycle spot `"G-0"` |
| `lot.park(14, "M-4", "motorcycle")` | returns `"G-0"` |
| `lot.find_vehicle(15, "M-4")` | returns `"G-0"` |
| `lot.find_vehicle(16, "M-1")` | returns `None`; `"M-1"` has left |
| `lot.unpark(17, "M-1")` | returns `None`; `"M-1"` is not parked |
