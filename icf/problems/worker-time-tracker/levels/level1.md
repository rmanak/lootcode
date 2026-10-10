Initially, the tracker does not know about any workers, so implement operations
to add workers, record every time a worker passes through the office door, and
report how much time each worker has spent in the office.

```python
add_worker(self, worker_id: str, position: str, compensation: int) -> bool
```

should add a new worker with the given id, position and compensation. Returns
`True` if the worker was successfully added, or `False` if a worker with
`worker_id` already exists — in which case the existing worker is left exactly
as it was.

```python
register(self, worker_id: str, timestamp: int) -> bool
```

should record that the worker passed through the office door at `timestamp`.
The calls for each worker alternate: the first `register` for a worker means
the worker **entered** the office, the next one means the worker **left**, the
one after that means the worker entered again, and so on. Each entry together
with the following exit forms one session. Returns `True` if the event was
recorded, or `False` if the worker doesn't exist — in which case nothing is
recorded.

```python
get_total_time(self, worker_id: str) -> int | None
```

should return the total time the worker has spent in the office: the sum of the
lengths of all the worker's completed sessions. A session that is still open —
the worker has entered but not left yet — does not count until the worker
leaves. Returns `0` for a worker with no completed sessions, or `None` if the
worker doesn't exist.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `wt = WorkerTimeTracker()` | a tracker with no workers |
| `wt.add_worker("ana", "Developer", 10)` | returns `True` |
| `wt.add_worker("ben", "Designer", 12)` | returns `True` |
| `wt.add_worker("ana", "Manager", 50)` | returns `False`; the worker `"ana"` already exists and is not changed |
| `wt.register("ana", 10)` | returns `True`; ana enters the office |
| `wt.register("ben", 15)` | returns `True`; ben enters the office |
| `wt.register("ana", 25)` | returns `True`; ana leaves, completing the session `[10, 25)` of length 15 |
| `wt.get_total_time("ana")` | returns `15` |
| `wt.get_total_time("ben")` | returns `0`; ben's session is still open |
| `wt.register("ana", 40)` | returns `True`; ana enters again |
| `wt.register("ben", 45)` | returns `True`; ben leaves, completing `[15, 45)` of length 30 |
| `wt.register("ana", 100)` | returns `True`; ana leaves, completing `[40, 100)` of length 60 |
| `wt.get_total_time("ana")` | returns `75`; 15 + 60 |
| `wt.get_total_time("ben")` | returns `30` |
| `wt.register("cy", 110)` | returns `False`; there is no worker `"cy"` |
| `wt.get_total_time("cy")` | returns `None` |
