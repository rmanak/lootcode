Parcels are carried by couriers, so implement operations to assign a courier to
a parcel, to let the courier carrying a parcel record events for it from the
road, and to list the parcels a courier is carrying. A parcel is carried by at
most one courier at a time; a courier may carry any number of parcels.
Couriers are not registered anywhere — a courier id simply appears when it is
first assigned.

```python
assign_courier(self, parcel_id: str, courier_id: str) -> bool
```

should make `courier_id` the courier of the parcel `parcel_id`, replacing the
courier it had before, if any. Returns `True` if the courier was assigned, or
`False` otherwise, in which case nothing changes. Specifically:

- Returns `False` if the parcel doesn't exist.
- Returns `False` if the parcel is already carried by `courier_id`.

```python
record_courier_event(self, courier_id: str, parcel_id: str, event_type: str, count: int) -> int | None
```

should record events exactly like `record_event`, but on behalf of a courier.
Returns the parcel's new tally for `event_type`, or `None` if the parcel
doesn't exist or is not currently carried by `courier_id` — in which case
nothing is recorded, and a missing parcel is **not** created. Events recorded
this way are ordinary events: they count in `get_event_count` and
`top_parcels` like any others.

```python
get_courier_parcels(self, courier_id: str) -> list[str]
```

should return the ids of the parcels currently carried by `courier_id`, in
lexicographical order. Returns an empty list if the courier carries nothing.

How the existing operations change:

- When `remove_event` deletes a parcel, its courier assignment is deleted with
  it. A parcel later re-created under the same id has no courier.
- Removing one event type of a parcel that still has others does not affect
  its courier.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `tracker = ParcelTracker()` | no parcels yet |
| `tracker.record_event("p1", "scanned", 1)` | returns `1` |
| `tracker.record_event("p2", "scanned", 1)` | returns `1` |
| `tracker.assign_courier("p1", "ann")` | returns `True` |
| `tracker.assign_courier("p2", "ann")` | returns `True` |
| `tracker.assign_courier("p9", "ann")` | returns `False`; there is no parcel `"p9"` |
| `tracker.get_courier_parcels("ann")` | returns `["p1", "p2"]` |
| `tracker.record_courier_event("ann", "p1", "delivered", 1)` | returns `1`; `"p1"` is assigned to ann |
| `tracker.record_courier_event("bob", "p1", "delivered", 1)` | returns `None`; bob does not carry `"p1"`, so nothing is recorded |
| `tracker.assign_courier("p1", "ann")` | returns `False`; ann already carries it |
| `tracker.assign_courier("p1", "bob")` | returns `True`; bob replaces ann |
| `tracker.get_courier_parcels("ann")` | returns `["p2"]` |
| `tracker.record_courier_event("bob", "p1", "delivered", 2)` | returns `3` |
| `tracker.top_parcels(2)` | returns `["p1(4)", "p2(1)"]`; courier events count like any other event |
