A board edited by a whole team needs an audit trail: when a task disappears or
its priority suddenly jumps, someone will ask what happened. The task board
should support looking up everything that happened to a task, and
reconstructing a task — or the whole list — as it was at an earlier moment.

These operations cover everything since the board was created, including every
operation from levels 1 to 3 that ran before any of them is called.

```python
get_task_history(self, timestamp: int, task_id: str) -> list[str] | None
```

should return every change made under the identifier `task_id`, oldest first,
as a list of strings in the format `"<timestamp>:<event>"`. The timestamp is the
one the change was made at, and the event is one of:

- `created` — a successful `create_task`;
- `updated` — a successful `update_task`;
- `assigned:<user_id>` — a successful `assign_task`, naming the user who now
  holds the task. A task moving from one user to another records only this one
  entry;
- `unassigned:<user_id>` — a successful `unassign_task`, naming the user who
  held the task;
- `deleted` — a successful `delete_task`. Deleting an assigned task records
  only this one entry.

Additional conditions:

- An operation that returns `False` records nothing.
- The history belongs to the identifier, not to a single task: it is kept after
  the task is deleted, and if the identifier is used again, the new task's
  changes are added after the old task's.
- Returns `None` if no task has ever been created with `task_id`.

For example, a task created at 1, assigned to `"ana"` at 3 and deleted at 6 has
the history `["1:created", "3:assigned:ana", "6:deleted"]`.

```python
get_task_at(self, timestamp: int, task_id: str, time_at: int) -> dict | None
```

should return the task with identifier `task_id` as it was at the moment
`time_at`, in the same form as `get_task`. Specifically:

- If an operation happened at exactly `time_at`, the result reflects the task
  after that operation.
- Returns `None` if no task with `task_id` existed at `time_at`: it had not been
  created yet, or it had been deleted at or before `time_at` and not created
  again since.
- If the identifier was used by more than one task, the result is the task that
  used it at `time_at`, with that task's own `created_at`.

```python
list_tasks_at(self, timestamp: int, time_at: int, limit: int) -> list[str]
```

should return what `list_tasks(limit)` would have returned at the moment
`time_at`: the tasks that existed then, with the priorities they had then, in
the order and format of level 2. A task deleted since is listed if it existed
at `time_at`; a task created after `time_at` is not. An operation at exactly
`time_at` is included. Returns an empty list if no task existed at `time_at`,
or if `limit` is `0`.

None of these operations change the board.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `board = TaskBoard()` | a board with no tasks and no users |
| `board.create_task(1, "bug", "Fix login bug", 3)` | returns `True` |
| `board.create_task(2, "docs", "Write docs", 1)` | returns `True` |
| `board.add_user(3, "ana", 1)` | returns `True` |
| `board.assign_task(4, "bug", "ana")` | returns `True` |
| `board.update_task(5, "bug", "Fix login bug now", 9)` | returns `True` |
| `board.assign_task(6, "docs", "ana")` | returns `False`; `"ana"`'s quota of 1 is full |
| `board.delete_task(7, "bug")` | returns `True` |
| `board.create_task(8, "bug", "Fix signup bug", 2)` | returns `True`; a new task that reuses the id |
| `board.get_task_history(9, "bug")` | returns `["1:created", "4:assigned:ana", "5:updated", "7:deleted", "8:created"]` |
| `board.get_task_history(10, "docs")` | returns `["2:created"]`; the refused assignment at 6 is not recorded |
| `board.get_task_history(11, "plan")` | returns `None`; no task was ever created with the id `"plan"` |
| `board.get_task_at(12, "bug", 4)` | returns `{"title": "Fix login bug", "priority": 3, "created_at": 1}` |
| `board.get_task_at(13, "bug", 5)` | returns `{"title": "Fix login bug now", "priority": 9, "created_at": 1}`; the update at exactly 5 is included |
| `board.get_task_at(14, "bug", 7)` | returns `None`; the task was deleted at 7 |
| `board.get_task_at(15, "bug", 8)` | returns `{"title": "Fix signup bug", "priority": 2, "created_at": 8}`; the new task |
| `board.get_task_at(16, "docs", 1)` | returns `None`; `"docs"` was created at 2 |
| `board.list_tasks_at(17, 3, 10)` | returns `["bug(3)", "docs(1)"]` |
| `board.list_tasks_at(18, 5, 10)` | returns `["bug(9)", "docs(1)"]`; the priority `"bug"` had at 5 |
| `board.list_tasks_at(19, 7, 10)` | returns `["docs(1)"]`; `"bug"` was deleted at 7 |
| `board.list_tasks_at(20, 20, 10)` | returns `["bug(2)", "docs(1)"]`; the same as `list_tasks(10)` right now |
| `board.list_tasks_at(21, 0, 10)` | returns `[]`; no task existed yet |
