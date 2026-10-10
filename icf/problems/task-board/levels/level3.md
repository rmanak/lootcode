Tasks are now picked up by the people on the team, and nobody can work on
everything at once. The task board should support registering users, each with
a quota of how many tasks they may hold at the same time, assigning a task to a
user and taking it back, and showing what a user is holding.

```python
add_user(self, timestamp: int, user_id: str, quota: int) -> bool
```

should register a new user who may hold at most `quota` tasks at any moment. A
user with a quota of `0` can never hold a task. Returns `True` if the user was
successfully added, or `False` if a user with `user_id` already exists — in
which case that user's quota does not change.

```python
assign_task(self, timestamp: int, task_id: str, user_id: str) -> bool
```

should assign the task `task_id` to the user `user_id`. A task is held by at
most one user at a time: if it is currently assigned to a different user, it
**moves** to `user_id`, and the previous user no longer holds it. Returns `True`
if the task was assigned, or `False` otherwise, in which case nothing changes.
Specifically:

- Returns `False` if the task doesn't exist.
- Returns `False` if the user doesn't exist.
- Returns `False` if the task is already assigned to `user_id`.
- Returns `False` if `user_id` already holds `quota` tasks. This includes a
  task that would move from another user: if the new user has no room, the task
  stays with the user who holds it.

```python
unassign_task(self, timestamp: int, task_id: str) -> bool
```

should take the task `task_id` back from the user who holds it, leaving it
unassigned. Returns `True` if the task was unassigned, or `False` if the task
doesn't exist or is not assigned to anyone.

```python
get_user_tasks(self, timestamp: int, user_id: str) -> list[str] | None
```

should return the tasks that `user_id` currently holds, in the same format and
the same order as `list_tasks`: by priority, descending, then by `created_at`,
ascending. When a task was assigned plays no part in the order. Returns an empty
list if the user holds no tasks, or `None` if the user doesn't exist.

### How the existing operations change

- `delete_task` also releases the task: its user holds one task fewer, and the
  slot is free immediately.
- `update_task` does not change who holds a task, but the new priority does
  change its place in `get_user_tasks`.
- A task created with an identifier that was used before is a new task, and it
  is not assigned to anyone — even if the deleted task was.

User ids and task ids are separate: a user may have the same id as a task.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `board = TaskBoard()` | a board with no tasks and no users |
| `board.create_task(1, "docs", "Write docs", 2)` | returns `True` |
| `board.create_task(2, "bug", "Fix login bug", 5)` | returns `True` |
| `board.create_task(3, "plan", "Plan sprint", 3)` | returns `True` |
| `board.add_user(4, "ana", 2)` | returns `True`; `"ana"` may hold 2 tasks |
| `board.add_user(5, "ana", 10)` | returns `False`; the user exists, and the quota stays 2 |
| `board.add_user(6, "ben", 1)` | returns `True` |
| `board.assign_task(7, "docs", "ana")` | returns `True` |
| `board.assign_task(8, "bug", "ana")` | returns `True` |
| `board.assign_task(9, "plan", "ana")` | returns `False`; `"ana"` already holds 2 tasks |
| `board.get_user_tasks(10, "ana")` | returns `["bug(5)", "docs(2)"]`; ordered like `list_tasks` |
| `board.assign_task(11, "bug", "ana")` | returns `False`; `"bug"` is already assigned to `"ana"` |
| `board.assign_task(12, "bug", "ben")` | returns `True`; `"bug"` moves from `"ana"` to `"ben"` |
| `board.get_user_tasks(13, "ana")` | returns `["docs(2)"]` |
| `board.assign_task(14, "plan", "ana")` | returns `True`; the move freed one of `"ana"`'s slots |
| `board.assign_task(15, "docs", "ben")` | returns `False`; `"ben"`'s quota of 1 is full, so `"docs"` stays with `"ana"` |
| `board.unassign_task(16, "bug")` | returns `True` |
| `board.unassign_task(17, "bug")` | returns `False`; `"bug"` is not assigned to anyone |
| `board.delete_task(18, "plan")` | returns `True`; the task is released, and `"ana"` holds one task fewer |
| `board.get_user_tasks(19, "ana")` | returns `["docs(2)"]` |
| `board.get_user_tasks(20, "ben")` | returns `[]`; `"ben"` holds nothing |
| `board.get_user_tasks(21, "cy")` | returns `None`; there is no user `"cy"` |
