A long task list is only useful if the important work is easy to find, so
implement operations to search tasks by name and to list tasks from the most to
the least important.

```python
search_tasks(self, timestamp: int, name_filter: str, max_results: int) -> list[str]
```

should return the ids of the tasks whose name contains `name_filter` anywhere in
it, sorted in the order described below, and at most `max_results` of them. The
match is case-sensitive, and an empty `name_filter` matches every task. Returns
an empty list if no task matches, or if `max_results` is `0` or less.

```python
list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]
```

should return the ids of all tasks, sorted in the order described below, and at
most `limit` of them. Returns an empty list if there are no tasks, or if `limit`
is `0` or less.

### Ordering

Both operations sort tasks by:

1. **priority, descending** — the most important task comes first;
2. **creation order, ascending** — among tasks with the same priority, the task
   that was created earlier comes first.

Creation order is the order in which `add_task` issued the ids, so
`"task_id_9"` comes before `"task_id_10"` even though the string `"task_id_10"`
is smaller. Updating a task changes its name and priority — and so its place in
the list — but never its creation order.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `tm = TaskManager()` | a task manager with no tasks |
| `tm.add_task(1, "Write report", 2)` | returns `"task_id_1"` |
| `tm.add_task(2, "Read report", 5)` | returns `"task_id_2"` |
| `tm.add_task(3, "Call supplier", 5)` | returns `"task_id_3"` |
| `tm.add_task(4, "Report bug", 1)` | returns `"task_id_4"` |
| `tm.list_tasks_sorted(5, 10)` | returns `["task_id_2", "task_id_3", "task_id_1", "task_id_4"]`; `"task_id_2"` and `"task_id_3"` share priority 5, so the one created first comes first |
| `tm.list_tasks_sorted(6, 2)` | returns `["task_id_2", "task_id_3"]` |
| `tm.search_tasks(7, "report", 10)` | returns `["task_id_2", "task_id_1"]`; `"Report bug"` does not match, because the search is case-sensitive |
| `tm.search_tasks(8, "report", 1)` | returns `["task_id_2"]` |
| `tm.search_tasks(9, "invoice", 5)` | returns `[]`; no name contains `"invoice"` |
| `tm.search_tasks(10, "", 0)` | returns `[]`; `max_results` is 0 |
| `tm.update_task(11, "task_id_4", "Report bug", 9)` | returns `True` |
| `tm.list_tasks_sorted(12, 10)` | returns `["task_id_4", "task_id_2", "task_id_3", "task_id_1"]`; the updated task now has the highest priority |
