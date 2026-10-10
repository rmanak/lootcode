### Instructions

Your task is to implement a simplified version of a worker time tracker — the
system behind the badge reader at an office door. Workers tap their badge when
they arrive and again when they leave. The system turns those taps into work
sessions, keeps track of how long everyone has spent in the office, and uses
that time to work out what each worker has earned. All operations that should
be supported by the tracker are described in the levels below.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `WorkerTimeTracker`. Plan your design according to the
level specifications below:

- **Level 1:** The worker time tracker should support adding workers, recording
  when they enter and leave the office, and reporting how much time each worker
  has spent there.
- **Level 2:** The worker time tracker should support ranking the workers in a
  position by the time they have spent in the office.
- **Level 3:** The worker time tracker should support promoting workers, and
  calculating the salary a worker earned during a period of time.
- **Level 4:** The worker time tracker should support double-pay periods,
  during which every worker earns twice their usual rate.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **worker** has a unique id, a position (such as `"Developer"`) and a
compensation: the amount of money the worker earns for each unit of time spent
in the office.

A worker's time is made of **sessions**. A session starts when the worker enters
the office and ends when the worker next leaves it. A session that started at
timestamp `enter` and ended at timestamp `leave` covers the half-open interval
`[enter, leave)`, so its length is `leave - enter`.

### Notes

- `register` is the only operation that happens at a moment in time. Its
  `timestamp` is a non-negative integer, and timestamps strictly increase from
  one `register` call to the next within a test. Every other operation simply
  happens in the order it is called.
- The `start_timestamp` and `end_timestamp` arguments introduced in levels 3
  and 4 describe a period of time. They are non-negative, `start_timestamp` is
  always less than `end_timestamp`, and the period may lie anywhere on the
  timeline — in the past, around the present, or after the last `register`.
- Worker ids and positions are non-empty, case-sensitive strings.
  Compensations are positive integers, so every amount of money is an integer.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `WorkerTimeTracker()` has no workers.
