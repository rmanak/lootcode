The office manager wants to know who actually comes in, so implement an
operation to rank the workers in a position by the time they have spent in the
office.

```python
top_n_workers(self, n: int, position: str) -> list[str]
```

should return the top `n` workers whose position is `position`, sorted by their
total time in the office in descending order. If two workers have spent the
same time, the one whose `worker_id` comes first alphabetically is listed first.
The result should be a list of strings in the following format:

```
["<worker_id_1>(<total_time_1>)", "<worker_id_2>(<total_time_2>)", ..., "<worker_id_n>(<total_time_n>)"]
```

Additional conditions:

- A worker's total time is exactly what `get_total_time` returns: completed
  sessions only.
- Every worker in the position appears in the ranking, including workers who
  have never completed a session — their total time is `0`.
- If fewer than `n` workers hold the position, return all of them. If nobody
  holds the position, or `n` is `0`, return an empty list. `n` is never
  negative.
- Positions are matched exactly, so `"developer"` is a different position from
  `"Developer"`.
- "Alphabetically" means ordinary string comparison, so `"w10"` comes before
  `"w9"`.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `wt = WorkerTimeTracker()` | a tracker with no workers |
| `wt.add_worker("ana", "Developer", 10)` | returns `True` |
| `wt.add_worker("ben", "Developer", 12)` | returns `True` |
| `wt.add_worker("cy", "Developer", 11)` | returns `True` |
| `wt.add_worker("dee", "Designer", 9)` | returns `True` |
| `wt.register("ana", 10)` | returns `True` |
| `wt.register("ben", 20)` | returns `True` |
| `wt.register("cy", 30)` | returns `True` |
| `wt.register("cy", 40)` | returns `True`; cy has spent 10 in the office |
| `wt.register("dee", 50)` | returns `True` |
| `wt.register("ana", 70)` | returns `True`; ana has spent 60 |
| `wt.register("ben", 80)` | returns `True`; ben has spent 60 |
| `wt.register("dee", 150)` | returns `True`; dee has spent 100 |
| `wt.top_n_workers(3, "Developer")` | returns `["ana(60)", "ben(60)", "cy(10)"]`; ana and ben are tied, so they are ordered by id |
| `wt.top_n_workers(2, "Developer")` | returns `["ana(60)", "ben(60)"]` |
| `wt.top_n_workers(5, "Designer")` | returns `["dee(100)"]`; only one worker holds this position |
| `wt.add_worker("eve", "Developer", 15)` | returns `True` |
| `wt.top_n_workers(10, "Developer")` | returns `["ana(60)", "ben(60)", "cy(10)", "eve(0)"]`; eve has not been in the office yet, but still appears |
| `wt.top_n_workers(3, "developer")` | returns `[]`; positions are case-sensitive |
