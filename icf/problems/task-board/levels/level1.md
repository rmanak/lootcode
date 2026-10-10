Initially, the task board is empty, so implement operations to create a task,
read it back, change it, and take it off the board once it is no longer
needed.

```python
create_task(self, timestamp: int, task_id: str, title: str, priority: int) -> bool
```

should create a new task with the given identifier, title and priority, created
at `timestamp`. Returns `True` if the task was successfully created, or `False`
if a task with `task_id` already exists — in which case the existing task is
left exactly as it was. An identifier that belonged to a task which has since
been deleted is free, so creating a task with it succeeds.

```python
get_task(self, timestamp: int, task_id: str) -> dict | None
```

should return the task with identifier `task_id`, in the form
`{"title": ..., "priority": ..., "created_at": ...}`, where `created_at` is the
timestamp of the `create_task` call that created it. Returns `None` if the task
doesn't exist.

```python
update_task(self, timestamp: int, task_id: str, title: str, priority: int) -> bool
```

should replace both the title and the priority of the task with identifier
`task_id`. Its `created_at` never changes. Returns `True` if the task was
successfully updated, or `False` if the task doesn't exist — in which case no
task is created. An update that sets the title and priority the task already
has still succeeds.

```python
delete_task(self, timestamp: int, task_id: str) -> bool
```

should remove the task with identifier `task_id` from the board. Returns `True`
if the task was successfully deleted, or `False` if the task doesn't exist.
Once deleted, the task can no longer be read, updated or deleted, and its
identifier is free for a new task.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `board = TaskBoard()` | a board with no tasks |
| `board.create_task(1, "t1", "Write report", 3)` | returns `True` |
| `board.create_task(2, "t2", "Email team", 1)` | returns `True` |
| `board.create_task(3, "t1", "Plan sprint", 5)` | returns `False`; the id `"t1"` is already in use, so nothing changes |
| `board.get_task(4, "t1")` | returns `{"title": "Write report", "priority": 3, "created_at": 1}` |
| `board.update_task(5, "t2", "Email the whole team", 2)` | returns `True` |
| `board.get_task(6, "t2")` | returns `{"title": "Email the whole team", "priority": 2, "created_at": 2}`; `created_at` is still the moment the task was created |
| `board.update_task(7, "t9", "Ghost", 1)` | returns `False`; there is no task `"t9"`, and none is created |
| `board.get_task(8, "t9")` | returns `None` |
| `board.delete_task(9, "t1")` | returns `True` |
| `board.delete_task(10, "t1")` | returns `False`; the task was already deleted |
| `board.get_task(11, "t1")` | returns `None` |
| `board.create_task(12, "t1", "Plan sprint", 5)` | returns `True`; the id is free again |
| `board.get_task(13, "t1")` | returns `{"title": "Plan sprint", "priority": 5, "created_at": 12}`; a brand-new task, with its own `created_at` |
