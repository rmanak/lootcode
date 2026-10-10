Parking is no longer free. The lot charges an hourly rate that depends on the
type of vehicle, and it needs to know what each vehicle owes, what each stay
cost after the vehicle has left, and how much money has been collected in
total.

A **stay** is one visit: it starts when `park` gives a vehicle a spot and ends
when `unpark` removes it. Its **fee** is:

```
fee = (number of started hours) * (the rate for the vehicle's type)
```

- An hour is `60 * 60 * 1000 = 3600000` milliseconds.
- The number of started hours is the stay's length divided by `3600000`,
  rounded **up**. A stay of exactly `3600000` milliseconds is 1 hour; one
  millisecond more is 2 hours. Every stay is at least 1 hour.
- The rate that applies is the one in force **when the vehicle parked**.
  Changing a rate later does not change what vehicles that are already parked
  will pay.

```python
set_rate(self, timestamp: int, vehicle_type: str, rate: int) -> None
```

should set the price per started hour for `vehicle_type` (`"motorcycle"`,
`"car"` or `"bus"`) for every vehicle of that type that parks from now on.
`rate` is a non-negative integer. Until a type's rate is set, vehicles of that
type park for free (their rate is `0`).

```python
get_fee(self, timestamp: int, plate: str) -> int | None
```

should return the fee the vehicle with licence plate `plate` would pay if it
left at `timestamp`. Returns `None` if no vehicle with this plate is parked.
Nothing changes: the vehicle stays where it is.

```python
get_history(self, timestamp: int, plate: str) -> list[str]
```

should return every **finished** stay of the vehicle with licence plate
`plate`, oldest first, each in the format `"<spot_id>(<fee>)"`, where
`spot_id` is the spot the vehicle had (the leftmost one, for a bus). A stay in
progress is not included. Returns an empty list if the vehicle has never
finished a stay.

```python
get_revenue(self, timestamp: int) -> int
```

should return the total of the fees of every finished stay in the lot. A stay
in progress does not count until the vehicle leaves.

### How the existing operations change

- `unpark` ends the stay: the vehicle is charged its fee at that moment, the
  stay is added to the vehicle's history, and the fee is added to the revenue.
  What `unpark` returns does not change.
- A `park` or `unpark` that returns `None` starts or ends no stay and charges
  nothing.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `lot = ParkingLot()` | a new lot with no levels |
| `lot.add_level(1, "G", "MRRRRRR")` | returns `True` |
| `lot.park(1000, "C-1", "car")` | returns `"G-1"`; no rate is set yet, so this stay is free |
| `lot.set_rate(2000, "car", 4)` | returns `None`; cars that park from now on pay 4 per started hour |
| `lot.set_rate(3000, "motorcycle", 1)` | returns `None` |
| `lot.park(4000, "C-2", "car")` | returns `"G-2"` |
| `lot.park(5000, "M-1", "motorcycle")` | returns `"G-0"` |
| `lot.get_fee(3600000, "C-2")` | returns `4`; the stay is under an hour so far, which counts as 1 started hour |
| `lot.get_fee(3604000, "C-2")` | returns `4`; exactly 3600000 milliseconds is still 1 hour |
| `lot.unpark(3605000, "M-1")` | returns `"G-0"`; the motorcycle is charged 1 hour at 1 |
| `lot.set_rate(3606000, "car", 10)` | returns `None`; cars already parked keep the rate of 4 |
| `lot.unpark(7300000, "C-2")` | returns `"G-2"`; 7296000 milliseconds is 3 started hours, at 4 each |
| `lot.unpark(7400000, "C-1")` | returns `"G-1"`; this car parked while cars were free, so it is charged 0 |
| `lot.get_history(7500000, "C-2")` | returns `["G-2(12)"]` |
| `lot.park(7600000, "C-2", "car")` | returns `"G-1"`; this new stay is charged the new rate of 10 |
| `lot.unpark(7700000, "C-2")` | returns `"G-1"` |
| `lot.get_history(7800000, "C-2")` | returns `["G-2(12)", "G-1(10)"]` |
| `lot.get_history(7900000, "BUS-9")` | returns `[]`; this vehicle has never finished a stay |
| `lot.get_fee(8000000, "C-2")` | returns `None`; `"C-2"` is not parked |
| `lot.get_revenue(8100000)` | returns `23`, which is 1 + 12 + 0 + 10 |
