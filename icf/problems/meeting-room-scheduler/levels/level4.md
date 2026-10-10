Plans change: a meeting sometimes has to move to a different time, and a room
sometimes has to close, for repairs for example. When a room closes, its
meetings should not simply disappear — the scheduler should find them another
room wherever it can. Implement both operations.

```python
reschedule(self, timestamp: int, meeting_id: str, start: int, end: int) -> bool
```

should move the meeting `meeting_id` to the new time `[start, end)`, **in the
same room**. Returns `True` if the meeting was moved, or `False` otherwise. A
call that returns `False` changes nothing. Specifically:

- Returns `False` if no meeting with this identifier is booked, including a
  cancelled one.
- Returns `False` if the new time overlaps **another** meeting in the same
  room. The meeting's own current time does not count, so a meeting may be
  moved to a time that overlaps where it was.
- The meeting keeps its identifier and its place in `last_booked`: moving a
  meeting does not make it a newer booking.

```python
close_room(self, timestamp: int, room_id: str) -> list[str] | None
```

should remove the room `room_id` and find a new room for each of its meetings.
Returns `None`, and changes nothing, if the room doesn't exist. Otherwise:

- The room's meetings are handled one at a time, in increasing order of
  `start`.
- Each meeting moves to the **first** remaining room, in the order the rooms
  were added, that is free for its time — the same choice `book_any` makes.
  It keeps its identifier, its time and its place in `last_booked`; only its
  room changes.
- A meeting that no remaining room is free for is cancelled.
- Returns the identifiers of the cancelled meetings, in the order they were
  handled. Returns an empty list if every meeting found a new room, or if the
  room had no meetings.

### How the existing operations change

- `get_meeting` shows a moved meeting's new time or new room.
- `busiest_rooms` counts a moved meeting's new length in its new room. A
  closed room no longer appears in the ranking.
- A meeting cancelled by `close_room` is cancelled like any other: `cancel`
  returns `False` for it and `get_meeting` returns `None`.
- After a room is closed its identifier is free, and `add_room` with that
  identifier adds a brand-new, empty room, which comes after every existing
  room in the order the rooms were added.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `scheduler = MeetingScheduler()` | a new scheduler with no rooms |
| `scheduler.add_room(1, "Alpha")` | returns `True` |
| `scheduler.add_room(2, "Beta")` | returns `True` |
| `scheduler.book_room(3, "Alpha", 100, 200)` | returns `"meeting1"` |
| `scheduler.book_room(4, "Alpha", 200, 260)` | returns `"meeting2"` |
| `scheduler.book_room(5, "Beta", 120, 180)` | returns `"meeting3"` |
| `scheduler.reschedule(6, "meeting2", 150, 210)` | returns `False`; it would overlap `"meeting1"` in `"Alpha"` |
| `scheduler.reschedule(7, "meeting2", 300, 400)` | returns `True` |
| `scheduler.reschedule(8, "meeting1", 50, 250)` | returns `True`; it overlaps its own old time, which is allowed |
| `scheduler.get_meeting(9, "meeting1")` | returns `"Alpha(50-250)"` |
| `scheduler.book_room(10, "Beta", 400, 450)` | returns `"meeting4"` |
| `scheduler.close_room(11, "Alpha")` | returns `["meeting1"]`; `"meeting1"` (from 50) is handled first and overlaps `"meeting3"` in `"Beta"`, so it is cancelled; `"meeting2"` (from 300) fits in `"Beta"`, because `"meeting4"` starts exactly when it ends |
| `scheduler.get_meeting(12, "meeting2")` | returns `"Beta(300-400)"` |
| `scheduler.get_meeting(13, "meeting1")` | returns `None` |
| `scheduler.busiest_rooms(14, 5)` | returns `["Beta(210)"]`; 60 + 100 + 50, and `"Alpha"` is gone |
| `scheduler.last_booked(15, 5)` | returns `["meeting4", "meeting3", "meeting2"]`; `"meeting2"` kept its place |
| `scheduler.close_room(16, "Alpha")` | returns `None`; the room is already closed |
| `scheduler.add_room(17, "Alpha")` | returns `True`; a new, empty room |
| `scheduler.free_rooms(18, 300, 400)` | returns `["Alpha"]`; `"Beta"` now holds `"meeting2"` |
