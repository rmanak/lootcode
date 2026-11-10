Dispatchers make mistakes, and couriers finish their shifts. Implement an
operation to undo the last courier change on a parcel, and one to sign a
courier out, releasing every parcel the courier is carrying.

A **courier change** on a parcel is anything that changes who carries it: a
successful `assign_courier`, or the parcel being released by `sign_out`. Each
parcel remembers its own courier changes, in order.

```python
undo_assignment(self, parcel_id: str) -> bool
```

should undo the most recent courier change on the parcel `parcel_id` that has
not been undone yet, giving the parcel back the courier it had just before
that change — or no courier, if it had none. Returns `True` if a change was
undone, or `False` if the parcel doesn't exist or has no changes left to undo.
Specifically:

- Calling it repeatedly walks further back through the parcel's changes, one
  at a time, until there are none left.
- An undone change is gone for good: there is no redo, and the change does not
  come back if a new one is made.
- A refused `assign_courier` (one that returned `False`) is not a change and
  cannot be undone.
- A parcel re-created after being deleted by `remove_event` starts with no
  changes to undo.

```python
sign_out(self, courier_id: str) -> int
```

should release every parcel currently carried by `courier_id`, so that each is
left with no courier. Returns the number of parcels released, which is `0` if
the courier carries nothing. Each release is a courier change on that parcel:
undoing it gives the parcel back to `courier_id`. Signing out does not stop a
courier from being assigned again later.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `tracker = ParcelTracker()` | no parcels yet |
| `tracker.record_event("p1", "scanned", 1)` | returns `1` |
| `tracker.record_event("p2", "scanned", 1)` | returns `1` |
| `tracker.assign_courier("p1", "ann")` | returns `True`; couriers: `{"p1": "ann"}` |
| `tracker.assign_courier("p1", "bob")` | returns `True`; couriers: `{"p1": "bob"}` |
| `tracker.assign_courier("p2", "bob")` | returns `True`; couriers: `{"p1": "bob", "p2": "bob"}` |
| `tracker.undo_assignment("p1")` | returns `True`; `"p1"` goes back to ann |
| `tracker.get_courier_parcels("ann")` | returns `["p1"]` |
| `tracker.sign_out("bob")` | returns `1`; `"p2"` is released; `"p1"` is no longer bob's |
| `tracker.get_courier_parcels("bob")` | returns `[]` |
| `tracker.record_courier_event("bob", "p2", "delivered", 1)` | returns `None`; bob carries nothing now |
| `tracker.undo_assignment("p2")` | returns `True`; undoing the release gives `"p2"` back to bob |
| `tracker.get_courier_parcels("bob")` | returns `["p2"]` |
| `tracker.undo_assignment("p2")` | returns `True`; `"p2"` had no courier before bob |
| `tracker.undo_assignment("p2")` | returns `False`; nothing left to undo |
| `tracker.undo_assignment("p1")` | returns `True`; back to no courier |
| `tracker.undo_assignment("p7")` | returns `False`; there is no parcel `"p7"` |
