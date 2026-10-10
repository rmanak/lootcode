Initially, the task manager does not contain any tasks, so implement operations
to create a task, change it, and read it back.

```python
add_task(self, timestamp: int, name: str, priority: int) -> str
```

should create a new task with the given name and priority, and return its id.
Ids are issued in creation order: `"task_id_1"` for the first task that is
added, `"task_id_2"` for the second, and so on. Adding a task never fails, even
if another task already has the same name.

```python
update_task(self, timestamp: int, task_id: str, name: str, priority: int) -> bool
```

should replace both the name and the priority of the task with id `task_id`.
Returns `True` if the task was successfully updated, or `False` if no task with
`task_id` exists — in which case nothing is created. The task keeps its id, and
an update never uses up an id.

```python
get_task(self, timestamp: int, task_id: str) -> str | None
```

should return the task with id `task_id` as a JSON string with no spaces, with
the name first and the priority second:

```
{"name":"<name>","priority":<priority>}
```

The priority is written as a plain integer, without quotes. Returns `None` if
no task with `task_id` exists.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `tm = TaskManager()` | a task manager with no tasks |
| `tm.add_task(1, "Write report", 3)` | returns `"task_id_1"` |
| `tm.add_task(2, "Email team", 1)` | returns `"task_id_2"` |
| `tm.add_task(3, "Email team", 4)` | returns `"task_id_3"`; two tasks may share a name, but not an id |
| `tm.get_task(4, "task_id_1")` | returns `'{"name":"Write report","priority":3}'` |
| `tm.update_task(5, "task_id_2", "Email the whole team", 2)` | returns `True` |
| `tm.get_task(6, "task_id_2")` | returns `'{"name":"Email the whole team","priority":2}'` |
| `tm.update_task(7, "task_id_9", "Ghost", 1)` | returns `False`; there is no task `"task_id_9"`, and none is created |
| `tm.get_task(8, "task_id_9")` | returns `None` |
| `tm.add_task(9, "Plan sprint", 5)` | returns `"task_id_4"`; the update did not use up an id |
