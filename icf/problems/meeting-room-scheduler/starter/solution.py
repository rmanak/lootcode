class MeetingScheduler:
    """Books meetings into a building's rooms.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: rooms and bookings --------------------------------------

    def add_room(self, timestamp: int, room_id: str) -> bool:
        pass

    def book_room(self, timestamp: int, room_id: str, start: int,
                  end: int) -> str | None:
        pass

    def cancel(self, timestamp: int, meeting_id: str) -> bool:
        pass

    def get_meeting(self, timestamp: int, meeting_id: str) -> str | None:
        pass

    # --- Level 2: finding a free room -------------------------------------

    def free_rooms(self, timestamp: int, start: int, end: int) -> list[str]:
        pass

    def book_any(self, timestamp: int, start: int, end: int) -> str | None:
        pass

    # --- Level 3: recent bookings and busy rooms --------------------------

    def last_booked(self, timestamp: int, n: int) -> list[str]:
        pass

    def busiest_rooms(self, timestamp: int, n: int) -> list[str]:
        pass

    # --- Level 4: rescheduling and closing rooms --------------------------

    def reschedule(self, timestamp: int, meeting_id: str, start: int,
                   end: int) -> bool:
        pass

    def close_room(self, timestamp: int, room_id: str) -> list[str] | None:
        pass
