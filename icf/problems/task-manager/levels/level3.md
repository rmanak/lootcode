Tasks are now handed to people, and nobody can work on everything at once. The
task manager should support registering users, each with a quota of how many
tasks they may be assigned at the same time, assigning a task to a user until a
deadline, and showing what a user is working on right now.

```python
add_user(self, timestamp: int, user_id: str, quota: int) -> bool
```

should register a new user who may hold at most `quota` active assignments at
any moment. The quota is a non-negative integer; a user with a quota of `0` can
never be assigned anything. Returns `True` if the user was successfully added,
or `False` if a user with `user_id` already exists — in which case that user's
quota does not change.

```python
assign_task(self, timestamp: int, task_id: str, user_id: str, finish_time: int) -> bool
```

should assign the task `task_id` to the user `user_id`, starting at `timestamp`
and ending at `finish_time`, which is always later than `timestamp`. The
assignment is **active** during the interval `[timestamp, finish_time)`: it is
active at any timestamp up to, but not including, `finish_time`, and at exactly
`finish_time` it expires on its own. Returns `True` if the assignment was
created, or `False` otherwise. Specifically:

- Returns `False` if no task with `task_id` exists.
- Returns `False` if no user with `user_id` exists.
- Returns `False` if the user already holds `quota` active assignments at
  `timestamp`.

Additional conditions:

- Only active assignments count against the quota. An assignment frees its
  slot at exactly its `finish_time`, without any call being needed.
- The same task can be assigned to several users, and even to the same user
  more than once. Every assignment is separate and takes its own slot.
- Updating a task does not change any of its assignments.

```python
get_user_tasks(self, timestamp: int, user_id: str) -> list[str]
```

should return the ids of the tasks assigned to `user_id` whose assignments are
active at `timestamp`. The ids are sorted by `finish_time`, ascending; when two
assignments finish at the same time, the one that was made earlier comes first.
A task assigned to the user more than once appears once for each active
assignment. Returns an empty list if the user doesn't exist or has no active
assignments.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `tm = TaskManager()` | a task manager with no tasks and no users |
| `tm.add_task(1, "Write report", 2)` | returns `"task_id_1"` |
| `tm.add_task(2, "Fix login bug", 5)` | returns `"task_id_2"` |
| `tm.add_task(3, "Plan sprint", 3)` | returns `"task_id_3"` |
| `tm.add_user(4, "ana", 2)` | returns `True`; `"ana"` may hold 2 active assignments |
| `tm.add_user(5, "ana", 10)` | returns `False`; the user exists, and the quota stays 2 |
| `tm.assign_task(6, "task_id_1", "ana", 50)` | returns `True`; active during `[6, 50)` |
| `tm.assign_task(7, "task_id_2", "ana", 20)` | returns `True`; active during `[7, 20)` |
| `tm.assign_task(8, "task_id_3", "ana", 30)` | returns `False`; `"ana"` already holds 2 active assignments |
| `tm.assign_task(9, "task_id_9", "ana", 30)` | returns `False`; there is no task `"task_id_9"` |
| `tm.get_user_tasks(10, "ana")` | returns `["task_id_2", "task_id_1"]`; the assignment finishing at 20 comes before the one finishing at 50 |
| `tm.get_user_tasks(20, "ana")` | returns `["task_id_1"]`; the assignment of `"task_id_2"` expired at exactly 20 |
| `tm.assign_task(21, "task_id_3", "ana", 50)` | returns `True`; the expired assignment freed its slot |
| `tm.get_user_tasks(22, "ana")` | returns `["task_id_1", "task_id_3"]`; both finish at 50, and `"task_id_1"` was assigned earlier |
| `tm.get_user_tasks(23, "ben")` | returns `[]`; there is no user `"ben"` |
