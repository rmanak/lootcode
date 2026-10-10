Workers get promoted, and the payroll team needs to know what everyone earned.
Implement an operation to promote a worker, and an operation to calculate the
salary a worker earned during a given period of time.

```python
promote(self, worker_id: str, new_position: str, new_compensation: int) -> bool
```

should promote the worker to `new_position` with `new_compensation`. The
promotion does **not** take effect immediately: it takes effect the **next time
the worker enters the office**. Until then the worker keeps their current
position and compensation — and if the worker is in the office when promoted,
the session in progress still finishes at the old compensation. Returns `True`
if the promotion was recorded, or `False` otherwise. Specifically:

- Returns `False` if the worker doesn't exist.
- Returns `False` if the worker already has a promotion that has not taken
  effect yet. Once that promotion takes effect, the worker can be promoted
  again.

Since `top_n_workers` ranks workers by their current position, a promoted worker
moves to the new position's ranking only when the promotion takes effect. The
worker's total time carries over: all the time spent in the office, in any
position, still counts.

```python
calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> int | None
```

should return the amount of money the worker earned during the period
`[start_timestamp, end_timestamp)`. For every completed session, only the part
of the session that falls inside the period is paid, at the compensation the
worker had when **that session started**:

```
paid time of a session = max(0, min(leave, end_timestamp) - max(enter, start_timestamp))
salary = sum over completed sessions of (paid time × compensation of that session)
```

Sessions outside the period earn nothing for it, and neither does a session
that is still open. Because a promotion only ever takes effect when a worker
enters, every session is paid at a single compensation. Returns `None` if the
worker doesn't exist.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `wt = WorkerTimeTracker()` | a tracker with no workers |
| `wt.add_worker("ana", "Junior Developer", 10)` | returns `True` |
| `wt.register("ana", 100)` | returns `True`; ana enters |
| `wt.register("ana", 200)` | returns `True`; the session `[100, 200)` is paid at 10 |
| `wt.promote("ana", "Senior Developer", 20)` | returns `True`; the promotion waits for ana's next entry |
| `wt.promote("ana", "Lead", 30)` | returns `False`; a promotion is already waiting to take effect |
| `wt.top_n_workers(5, "Junior Developer")` | returns `["ana(100)"]`; the promotion has not taken effect yet |
| `wt.register("ana", 300)` | returns `True`; ana enters, and the promotion takes effect now |
| `wt.top_n_workers(5, "Senior Developer")` | returns `["ana(100)"]`; the earlier time carries over |
| `wt.register("ana", 400)` | returns `True`; the session `[300, 400)` is paid at 20 |
| `wt.calc_salary("ana", 0, 500)` | returns `3000`; 100 × 10 + 100 × 20 |
| `wt.calc_salary("ana", 150, 350)` | returns `1500`; 50 × 10 from the first session, 50 × 20 from the second |
| `wt.calc_salary("ana", 200, 300)` | returns `0`; ana was not in the office during this period |
| `wt.promote("ana", "Lead", 30)` | returns `True`; the previous promotion has taken effect |
| `wt.register("ana", 500)` | returns `True`; ana enters as Lead, paid at 30 |
| `wt.promote("ana", "Director", 40)` | returns `True`; promoted while in the office |
| `wt.register("ana", 600)` | returns `True`; the session `[500, 600)` still finishes at 30 |
| `wt.calc_salary("ana", 0, 1000)` | returns `6000`; 1000 + 2000 + 100 × 30 |
| `wt.calc_salary("bob", 0, 10)` | returns `None`; there is no worker `"bob"` |
