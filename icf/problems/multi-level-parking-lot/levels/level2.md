Drivers want to know where there is room before they drive up the ramps, so
implement operations that count the free spots on a level and rank the levels
by how many free spots they have — the numbers shown on the display board at
the entrance.

```python
count_free(self, timestamp: int, level_id: str, spot_type: str) -> int | None
```

should return how many spots of type `spot_type` are free on the level
`level_id`. `spot_type` is `"M"` or `"R"`. Returns `None` if the level doesn't
exist.

```python
top_levels(self, timestamp: int, n: int) -> list[str]
```

should return the top `n` levels with the most free spots, counting spots of
both types together, sorted in descending order of that count. If two levels
have the same number of free spots, the one whose `level_id` comes first
alphabetically is listed first. The result should be a list of strings in the
following format:

```
["<level_id_1>(<free_spots_1>)", "<level_id_2>(<free_spots_2>)", ..., "<level_id_n>(<free_spots_n>)"]
```

Additional conditions:

- Every level appears in the ranking, including a full level — its count is
  `0`.
- If fewer than `n` levels exist, return all of them. If `n` is `0`, or the lot
  has no levels, return an empty list.
- "Alphabetically" means ordinary string comparison, so `"B1"` comes before
  `"G"` and `"P10"` comes before `"P2"`. This ordering is only for breaking
  ties in the ranking — parking still searches levels in the order they were
  added.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `lot = ParkingLot()` | a new lot with no levels |
| `lot.add_level(1, "G", "MRRR")` | returns `True` |
| `lot.add_level(2, "P1", "MMRR")` | returns `True` |
| `lot.add_level(3, "P2", "R")` | returns `True` |
| `lot.park(4, "C-1", "car")` | returns `"G-1"` |
| `lot.park(5, "C-2", "car")` | returns `"G-2"` |
| `lot.park(6, "M-1", "motorcycle")` | returns `"G-0"` |
| `lot.count_free(7, "G", "R")` | returns `1`; only `"G-3"` is free |
| `lot.count_free(8, "G", "M")` | returns `0` |
| `lot.count_free(9, "P1", "M")` | returns `2` |
| `lot.count_free(10, "B2", "R")` | returns `None`; there is no level `"B2"` |
| `lot.top_levels(11, 2)` | returns `["P1(4)", "G(1)"]`; `"G"` and `"P2"` are tied at 1, and `"G"` comes first alphabetically |
| `lot.top_levels(12, 5)` | returns `["P1(4)", "G(1)", "P2(1)"]`; only three levels exist |
| `lot.unpark(13, "C-1")` | returns `"G-1"` |
| `lot.top_levels(14, 3)` | returns `["P1(4)", "G(2)", "P2(1)"]` |
| `lot.top_levels(15, 0)` | returns `[]` |
