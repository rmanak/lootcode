A long board is only useful if the most important work is easy to find, so
implement an operation that lists the tasks from the most to the least
important.

```python
list_tasks(self, timestamp: int, limit: int) -> list[str]
```

should return the tasks currently on the board, sorted in the order described
below, and at most `limit` of them. The result should be a list of strings in
the following format:

```
["<task_id_1>(<priority_1>)", "<task_id_2>(<priority_2>)", ..., "<task_id_n>(<priority_n>)"]
```

If fewer than `limit` tasks exist, return all of them. Returns an empty list if
the board has no tasks, or if `limit` is `0`.

### Ordering

Tasks are sorted by:

1. **priority, descending** — the most important task comes first;
2. **`created_at`, ascending** — among tasks with the same priority, the task
   that was created earlier comes first.

Additional conditions:

- Deleted tasks are not listed.
- The identifier plays no part in the ordering: if `"zulu"` was created before
  `"alpha"` with the same priority, `"zulu"` comes first.
- Updating a task changes its priority — and so its place in the list — but
  never its `created_at`. Among the tasks that share its new priority, it sits
  where its creation time puts it.
- A task created with an identifier that was used before is a new task: its
  `created_at` is the moment it was created again, so it comes after every
  older task with the same priority.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `board = TaskBoard()` | a board with no tasks |
| `board.create_task(1, "write", "Write report", 2)` | returns `True` |
| `board.create_task(2, "read", "Read report", 5)` | returns `True` |
| `board.create_task(3, "call", "Call supplier", 5)` | returns `True` |
| `board.create_task(4, "bug", "Fix bug", 1)` | returns `True` |
| `board.list_tasks(5, 10)` | returns `["read(5)", "call(5)", "write(2)", "bug(1)"]`; `"read"` and `"call"` share priority 5, and `"read"` was created first |
| `board.list_tasks(6, 2)` | returns `["read(5)", "call(5)"]` |
| `board.update_task(7, "bug", "Fix login bug", 5)` | returns `True` |
| `board.list_tasks(8, 10)` | returns `["read(5)", "call(5)", "bug(5)", "write(2)"]`; `"bug"` now has priority 5, and it was created after the other two |
| `board.delete_task(9, "read")` | returns `True` |
| `board.create_task(10, "read", "Re-read report", 5)` | returns `True` |
| `board.list_tasks(11, 10)` | returns `["call(5)", "bug(5)", "read(5)", "write(2)"]`; the new `"read"` was created at 10, so it comes last among the tasks with priority 5 |
| `board.list_tasks(12, 0)` | returns `[]` |
