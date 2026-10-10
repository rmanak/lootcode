Initially, the building has no rooms on the system, so implement operations to
add rooms, book a meeting in a particular room, cancel a meeting, and look a
meeting up. This is the core of the scheduler — every later level builds on
the meetings booked here.

```python
add_room(self, timestamp: int, room_id: str) -> bool
```

should add a new room with the given identifier and no meetings. Returns
`True` if the room was added, or `False` if a room with `room_id` already
exists — in which case the existing room and its meetings are left exactly as
they were.

```python
book_room(self, timestamp: int, room_id: str, start: int, end: int) -> str | None
```

should book a meeting in the room `room_id` from `start` to `end`, and return
the new meeting's identifier. Returns `None`, and books nothing, if:

- the room `room_id` doesn't exist, or
- the new meeting would overlap a meeting already booked in that room.

Meetings in different rooms never conflict with each other.

```python
cancel(self, timestamp: int, meeting_id: str) -> bool
```

should cancel the meeting `meeting_id`, which frees its time in its room.
Returns `True` if the meeting was cancelled, or `False` if no meeting with this
identifier is booked — including a meeting that has already been cancelled.

```python
get_meeting(self, timestamp: int, meeting_id: str) -> str | None
```

should return where and when the meeting `meeting_id` takes place, as a string
in the format `"<room_id>(<start>-<end>)"`, such as `"Alpha(600-660)"`. Returns
`None` if no meeting with this identifier is booked, including a cancelled
one.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `scheduler = MeetingScheduler()` | a new scheduler with no rooms |
| `scheduler.add_room(1, "Alpha")` | returns `True` |
| `scheduler.add_room(2, "Alpha")` | returns `False`; the room `"Alpha"` already exists |
| `scheduler.add_room(3, "Beta")` | returns `True` |
| `scheduler.book_room(4, "Alpha", 600, 660)` | returns `"meeting1"` |
| `scheduler.book_room(5, "Alpha", 630, 700)` | returns `None`; it overlaps `"meeting1"` from 630 to 660 |
| `scheduler.book_room(6, "Alpha", 660, 720)` | returns `"meeting2"`; it starts exactly when `"meeting1"` ends, which is not an overlap |
| `scheduler.book_room(7, "Beta", 630, 700)` | returns `"meeting3"`; `"Beta"` is a different room |
| `scheduler.book_room(8, "Gamma", 600, 660)` | returns `None`; there is no room `"Gamma"` |
| `scheduler.get_meeting(9, "meeting2")` | returns `"Alpha(660-720)"` |
| `scheduler.cancel(10, "meeting1")` | returns `True` |
| `scheduler.cancel(11, "meeting1")` | returns `False`; it is already cancelled |
| `scheduler.get_meeting(12, "meeting1")` | returns `None` |
| `scheduler.book_room(13, "Alpha", 540, 660)` | returns `"meeting4"`; the cancelled meeting no longer blocks the room, and the failed bookings did not use up a number |
| `scheduler.get_meeting(14, "meeting4")` | returns `"Alpha(540-660)"` |
| `scheduler.cancel(15, "meeting9")` | returns `False`; there is no such meeting |
