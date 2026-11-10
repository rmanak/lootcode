The operations team wants to see which parcels need the most handling, so
implement an operation that ranks parcels by their **total** number of events
— the sum of the tallies of all their event types.

```python
top_parcels(self, n: int) -> list[str]
```

should return the top `n` parcels with the highest totals, in the following
format:

```
["<parcel_id_1>(<total_1>)", "<parcel_id_2>(<total_2>)", ..., "<parcel_id_n>(<total_n>)"]
```

Additional conditions:

- Parcels are sorted in descending order of their totals or, in the case of
  ties, in lexicographical order of their ids — ordinary Python string
  comparison, so `"P1"` comes before `"p1"` and `"p10"` before `"p9"`.
- Every existing parcel is ranked. Removed event types no longer count, and a
  parcel deleted by `remove_event` is not listed.
- If fewer than `n` parcels exist, return all of them. If `n` is `0`, or there
  are no parcels, return an empty list.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `tracker = ParcelTracker()` | no parcels yet |
| `tracker.record_event("p1", "scanned", 2)` | returns `2` |
| `tracker.record_event("p2", "scanned", 1)` | returns `1` |
| `tracker.record_event("p2", "delayed", 4)` | returns `4` |
| `tracker.record_event("p3", "scanned", 3)` | returns `3` |
| `tracker.record_event("p0", "scanned", 3)` | returns `3`; totals: `{"p1": 2, "p2": 5, "p3": 3, "p0": 3}` |
| `tracker.top_parcels(3)` | returns `["p2(5)", "p0(3)", "p3(3)"]`; `"p0"` and `"p3"` are tied at 3, so the smaller id comes first |
| `tracker.remove_event("p2", "delayed")` | returns `True`; `"p2"` is down to 1 |
| `tracker.top_parcels(10)` | returns `["p0(3)", "p3(3)", "p1(2)", "p2(1)"]`; only four parcels exist |
| `tracker.top_parcels(0)` | returns `[]` |
