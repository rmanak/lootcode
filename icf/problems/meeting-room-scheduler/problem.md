### Instructions

Your task is to implement a simplified version of a meeting room scheduler.
An office building has a set of meeting rooms, and people book them for
meetings: they ask for a particular room, or for any room that is free at the
time they need. The system you are building is the calendar behind those
requests — it never lets two meetings overlap in the same room, and it keeps
every meeting where people can find it, even when a meeting moves or a room
closes. Everything is kept in memory, and every operation carries the
timestamp at which it happens.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `MeetingScheduler`. Plan your design according to the
level specifications below:

- **Level 1:** The scheduler should support adding rooms, booking a meeting in
  a particular room, cancelling a meeting, and looking a meeting up.
- **Level 2:** The scheduler should support finding the rooms that are free
  for a given time, and booking whichever room is free first.
- **Level 3:** The scheduler should support listing the most recent bookings
  and ranking rooms by how much time is booked in them.
- **Level 4:** The scheduler should support moving a meeting to a new time and
  closing a room, rehousing its meetings in other rooms where possible.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **room** has an identifier, such as `"Alpha"`.

A **meeting** takes place in one room from `start` to `end`. The two times are
whole numbers of minutes on the building's calendar, with `start < end`. A
meeting occupies the **half-open** interval `[start, end)`: it includes the
minute `start` but not the minute `end`. So a meeting from `600` to `660` and
one from `660` to `720` do **not** overlap, and may be booked in the same room
one after the other.

Every successful booking gets an identifier `"meeting<k>"`, where `k` counts
the successful bookings made so far: the first is `"meeting1"`, the next
`"meeting2"`, and so on. A booking that fails does not use up a number, and an
identifier is never reused, even after its meeting is cancelled.

### Notes

- `timestamp` is when the call is made. It is a non-negative integer measured
  in milliseconds, and it strictly increases from one call to the next within a
  test. It is unrelated to a meeting's `start` and `end`: a meeting may be
  booked for any time.
- It is guaranteed that `0 <= start < end` in every call that takes them.
- Room identifiers are non-empty strings of letters and digits.
- A fresh `MeetingScheduler()` has no rooms and no meetings.
