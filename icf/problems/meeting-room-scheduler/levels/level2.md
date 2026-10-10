Most people don't care which room they get, as long as it is free when they
need it. Implement an operation that lists the rooms free for a given time,
and one that books the first of them.

In this level, "free for `[start, end)`" means that the room has no meeting
that overlaps `[start, end)`. Rooms are always considered **in the order they
were added**.

```python
free_rooms(self, timestamp: int, start: int, end: int) -> list[str]
```

should return the identifiers of every room that is free for `[start, end)`,
in the order the rooms were added. Returns an empty list if no room is free.

```python
book_any(self, timestamp: int, start: int, end: int) -> str | None
```

should book a meeting from `start` to `end` in the **first** room, in the order
the rooms were added, that is free for that time, and return the new meeting's
identifier. Returns `None`, and books nothing, if no room is free. A meeting
booked this way is an ordinary meeting: `get_meeting` shows the room it was
given, and `cancel` works on it as before.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `scheduler = MeetingScheduler()` | a new scheduler with no rooms |
| `scheduler.add_room(1, "Alpha")` | returns `True` |
| `scheduler.add_room(2, "Beta")` | returns `True` |
| `scheduler.add_room(3, "Gamma")` | returns `True` |
| `scheduler.book_room(4, "Alpha", 540, 600)` | returns `"meeting1"` |
| `scheduler.book_room(5, "Beta", 570, 630)` | returns `"meeting2"` |
| `scheduler.free_rooms(6, 540, 600)` | returns `["Gamma"]`; `"Alpha"` and `"Beta"` both have a meeting in that time |
| `scheduler.free_rooms(7, 600, 630)` | returns `["Alpha", "Gamma"]`; `"meeting1"` ends at 600, so `"Alpha"` is free from 600 |
| `scheduler.book_any(8, 560, 620)` | returns `"meeting3"`, in `"Gamma"`, the only room free for that time |
| `scheduler.book_any(9, 600, 660)` | returns `"meeting4"`, in `"Alpha"`, the first free room in the order the rooms were added |
| `scheduler.book_any(10, 580, 600)` | returns `None`; every room has a meeting at 580 |
| `scheduler.get_meeting(11, "meeting4")` | returns `"Alpha(600-660)"` |
| `scheduler.free_rooms(12, 590, 600)` | returns `[]` |
