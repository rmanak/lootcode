"""Checkpoint: the reference solution after levels 1-3 (no rescheduling or closing yet)."""

from dataclasses import dataclass, field


@dataclass(slots=True, eq=False)     # a meeting is an identity, not a value
class Meeting:
    meeting_id: str
    room: "Room"
    start: int
    end: int
    booked: int                      # booking order: 1 for the first booking
    active: bool = True

    @property
    def length(self) -> int:
        return self.end - self.start

    def overlaps(self, start: int, end: int) -> bool:
        """Half-open intervals: touching at an endpoint is not an overlap."""
        return self.start < end and start < self.end

    def describe(self) -> str:
        return f"{self.room.room_id}({self.start}-{self.end})"


@dataclass(slots=True, eq=False)
class Room:
    room_id: str
    meetings: list[Meeting] = field(default_factory=list)   # active only

    def is_free(self, start: int, end: int) -> bool:
        return not any(meeting.overlaps(start, end) for meeting in self.meetings)

    @property
    def booked_time(self) -> int:
        return sum(meeting.length for meeting in self.meetings)


class MeetingScheduler:
    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}          # insertion order = search order
        self._meetings: dict[str, Meeting] = {}    # every meeting ever booked
        self._bookings = 0

    # --- helpers -----------------------------------------------------------

    def _active(self, meeting_id: str) -> Meeting | None:
        meeting = self._meetings.get(meeting_id)
        return meeting if meeting is not None and meeting.active else None

    def _first_free(self, start: int, end: int) -> Room | None:
        for room in self._rooms.values():
            if room.is_free(start, end):
                return room
        return None

    def _book(self, room: Room, start: int, end: int) -> str:
        self._bookings += 1
        meeting = Meeting(f"meeting{self._bookings}", room, start, end,
                          self._bookings)
        self._meetings[meeting.meeting_id] = meeting
        room.meetings.append(meeting)
        return meeting.meeting_id

    # --- Level 1 -----------------------------------------------------------

    def add_room(self, timestamp: int, room_id: str) -> bool:
        if room_id in self._rooms:
            return False
        self._rooms[room_id] = Room(room_id)
        return True

    def book_room(self, timestamp: int, room_id: str, start: int,
                  end: int) -> str | None:
        room = self._rooms.get(room_id)
        if room is None or not room.is_free(start, end):
            return None
        return self._book(room, start, end)

    def cancel(self, timestamp: int, meeting_id: str) -> bool:
        meeting = self._active(meeting_id)
        if meeting is None:
            return False
        meeting.active = False
        meeting.room.meetings.remove(meeting)
        return True

    def get_meeting(self, timestamp: int, meeting_id: str) -> str | None:
        meeting = self._active(meeting_id)
        return None if meeting is None else meeting.describe()

    # --- Level 2 -----------------------------------------------------------

    def free_rooms(self, timestamp: int, start: int, end: int) -> list[str]:
        return [room.room_id for room in self._rooms.values()
                if room.is_free(start, end)]

    def book_any(self, timestamp: int, start: int, end: int) -> str | None:
        room = self._first_free(start, end)
        return None if room is None else self._book(room, start, end)

    # --- Level 3 -----------------------------------------------------------

    def last_booked(self, timestamp: int, n: int) -> list[str]:
        active = [meeting for meeting in self._meetings.values() if meeting.active]
        active.sort(key=lambda meeting: -meeting.booked)
        return [meeting.meeting_id for meeting in active[:n]]

    def busiest_rooms(self, timestamp: int, n: int) -> list[str]:
        ranked = sorted(self._rooms.values(),
                        key=lambda room: (-room.booked_time, room.room_id))
        return [f"{room.room_id}({room.booked_time})" for room in ranked[:n]]
