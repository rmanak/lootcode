The office manager wants to see what was booked most recently, and which rooms
are in the highest demand, so implement an operation that lists the latest
bookings and one that ranks rooms by how much time is booked in them.

```python
last_booked(self, timestamp: int, n: int) -> list[str]
```

should return the identifiers of the `n` most recently booked meetings that
are still booked, **newest first**. "Most recently booked" is about when the
booking was made, which is the order of the meeting numbers — not about the
meetings' `start` times. Additional conditions:

- Cancelled meetings are skipped, so the list may reach further back to find
  `n` meetings.
- If fewer than `n` meetings are booked, return all of them. If `n` is `0`, or
  nothing is booked, return an empty list.

```python
busiest_rooms(self, timestamp: int, n: int) -> list[str]
```

should return the top `n` rooms with the most **booked time**, sorted in
descending order of that time. A room's booked time is the total length
(`end - start`) of all the meetings booked in it; cancelled meetings don't
count. If two rooms have the same booked time, the one whose `room_id` comes
first alphabetically is listed first. The result should be a list of strings
in the following format:

```
["<room_id_1>(<booked_time_1>)", "<room_id_2>(<booked_time_2>)", ..., "<room_id_n>(<booked_time_n>)"]
```

Additional conditions:

- Every room appears in the ranking, including rooms with nothing booked —
  their booked time is `0`.
- If fewer than `n` rooms exist, return all of them. If `n` is `0`, or there
  are no rooms, return an empty list.
- "Alphabetically" means ordinary string comparison, so `"B2"` comes before
  `"a1"`. This ordering is only for breaking ties in the ranking — `book_any`
  and `free_rooms` still use the order the rooms were added.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `scheduler = MeetingScheduler()` | a new scheduler with no rooms |
| `scheduler.add_room(1, "Beta")` | returns `True` |
| `scheduler.add_room(2, "Alpha")` | returns `True` |
| `scheduler.add_room(3, "Gamma")` | returns `True` |
| `scheduler.book_room(4, "Alpha", 0, 90)` | returns `"meeting1"` |
| `scheduler.book_any(5, 0, 30)` | returns `"meeting2"`, in `"Beta"`, the first room added |
| `scheduler.book_room(6, "Gamma", 100, 190)` | returns `"meeting3"` |
| `scheduler.book_any(7, 60, 150)` | returns `"meeting4"`, in `"Beta"` |
| `scheduler.last_booked(8, 2)` | returns `["meeting4", "meeting3"]` |
| `scheduler.busiest_rooms(9, 3)` | returns `["Beta(120)", "Alpha(90)", "Gamma(90)"]`; `"Beta"` has 30 + 90 booked, and the tie at 90 is broken alphabetically |
| `scheduler.cancel(10, "meeting4")` | returns `True` |
| `scheduler.last_booked(11, 10)` | returns `["meeting3", "meeting2", "meeting1"]`; the cancelled meeting is skipped |
| `scheduler.busiest_rooms(12, 2)` | returns `["Alpha(90)", "Gamma(90)"]`; `"Beta"` is down to 30 |
| `scheduler.last_booked(13, 0)` | returns `[]` |
