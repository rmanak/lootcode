### Instructions

Your task is to implement a simplified version of a task board — the shared
list a team uses to keep track of the work in front of it. People put tasks on
the board, each with a title and a priority, change them as plans change, and
take them off once they are no longer needed. Team members pick tasks up, but
nobody can hold more than a set number at once. And because the board is edited
by many hands, it also has to be able to say what happened to a task, and what
the board looked like at an earlier moment. Everything is kept in memory, and
every operation carries the timestamp at which it happens.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `TaskBoard`. Plan your design according to the level
specifications below:

- **Level 1:** The task board should support creating, reading, updating and
  deleting tasks.
- **Level 2:** The task board should support listing tasks from the most to the
  least important.
- **Level 3:** The task board should support users who may only hold a limited
  number of tasks at once, and assigning tasks to them.
- **Level 4:** The task board should support looking up everything that
  happened to a task, and what a task or the whole board looked like at an
  earlier moment.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **task** has an identifier, a title, a priority, and the timestamp at which it
was created. The identifier is chosen by the caller, and only one task may use
it at a time. Once a task is deleted its identifier is free again, and a task
created with it later is a brand-new task. A higher priority number means a more
important task.

Whenever a task is returned, it is a dictionary of the form:

```python
{"title": "Write report", "priority": 3, "created_at": 1}
```

### Notes

- Timestamps are non-negative integers, and they strictly increase from one call
  to the next within a test. The only exception is the `time_at` argument
  introduced in level 4, which names a moment that is never later than
  `timestamp`.
- Task ids, titles and user ids are non-empty strings, compared exactly, so
  `"t1"` and `"T1"` are different ids. Several tasks may share a title. User ids
  never contain a colon `:`.
- Priorities are integers and may be zero or negative. Quotas and limits are
  non-negative integers.
- A dictionary or list you return belongs to the caller: changing it must not
  change the board.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `TaskBoard()` has no tasks and no users.
