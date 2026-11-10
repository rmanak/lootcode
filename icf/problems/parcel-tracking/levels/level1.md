Initially, the tracking system knows no parcels, so implement operations to
record events for a parcel, read the tally of one event type, and remove an
event type that was recorded by mistake.

```python
record_event(self, parcel_id: str, event_type: str, count: int) -> int
```

should add `count` events of type `event_type` to the parcel `parcel_id`. If
the parcel doesn't exist yet, it is created; if it has no tally for
`event_type` yet, the tally starts at `0`. Returns the parcel's new tally for
`event_type`.

```python
get_event_count(self, parcel_id: str, event_type: str) -> int | None
```

should return the parcel's tally for `event_type`. Returns `None` if the parcel
doesn't exist, or if it has no events of that type.

```python
remove_event(self, parcel_id: str, event_type: str) -> bool
```

should remove the tally for `event_type` from the parcel `parcel_id`
altogether. Returns `True` if it was removed, or `False` if the parcel doesn't
exist or has no events of that type. If the removed event type was the
parcel's last one, **the parcel itself is deleted**: it no longer exists, and a
later `record_event` for the same `parcel_id` creates a brand-new parcel.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `tracker = ParcelTracker()` | no parcels yet |
| `tracker.record_event("p1", "scanned", 2)` | returns `2`; the parcel `"p1"` is created |
| `tracker.record_event("p1", "scanned", 3)` | returns `5`; 2 + 3 |
| `tracker.record_event("p1", "delayed", 1)` | returns `1`; a different event type has its own tally; events: `{"p1": {"scanned": 5, "delayed": 1}}` |
| `tracker.get_event_count("p1", "scanned")` | returns `5` |
| `tracker.get_event_count("p1", "lost")` | returns `None`; `"p1"` has no `"lost"` events |
| `tracker.get_event_count("p2", "scanned")` | returns `None`; there is no parcel `"p2"` |
| `tracker.remove_event("p1", "scanned")` | returns `True`; events: `{"p1": {"delayed": 1}}` |
| `tracker.remove_event("p1", "scanned")` | returns `False`; already removed |
| `tracker.remove_event("p1", "delayed")` | returns `True`; that was the last event type, so `"p1"` is deleted; events: `{}` |
| `tracker.record_event("p1", "scanned", 4)` | returns `4`; `"p1"` starts again from nothing |
