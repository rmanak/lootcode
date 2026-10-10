### Instructions

Your task is to implement a simplified version of a task manager — the kind of
tool a team uses to keep track of its work. People create tasks and give each
one a priority, look up the most important ones, hand tasks to teammates with a
deadline, and mark them as done. The system you are building keeps that list in
memory and answers questions about it. Every operation carries the timestamp at
which it happens.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `TaskManager`. Plan your design according to the level
specifications below:

- **Level 1:** The task manager should support creating tasks, updating them,
  and reading them back.
- **Level 2:** The task manager should support searching tasks by name and
  listing tasks in order of priority.
- **Level 3:** The task manager should support users who may only work on a
  limited number of tasks at once, and assigning a task to a user until a
  deadline.
- **Level 4:** The task manager should support completing assigned tasks, and
  reporting the assignments that reached their deadline without being
  completed.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **task** has an id, a name and a priority. Ids are issued by the task manager
itself, in creation order: `"task_id_1"` for the first task, `"task_id_2"` for
the second, and so on. Several tasks may share the same name, but every task has
its own id. A higher priority number means a more important task.

### Notes

- Every operation takes a `timestamp`: a non-negative integer that strictly
  increases from one call to the next within a test. Levels 1 and 2 do not
  need it, but levels 3 and 4 do.
- Task names are non-empty strings, and they never contain a double quote `"`
  or a backslash `\`. Priorities are integers and may be zero or negative.
- Tasks are never deleted.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `TaskManager()` has no tasks and no users.
