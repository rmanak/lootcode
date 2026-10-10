"""Level 3 — recent bookings and busy rooms (visible cases)."""
from icf_testkit import case, expect

@case("last_booked lists the newest bookings first")
def last_booked_basic(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 500, 510)
    s.book_room(3, "A", 0, 10)
    s.book_room(4, "A", 300, 310)
    expect(s.last_booked(5, 2), ["meeting3", "meeting2"], "booking order, not start time")


@case("last_booked skips cancelled meetings and returns everything if n is large")
def last_booked_cancelled(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    for k in range(3):
        s.book_room(2 + k, "A", 10 * k, 10 * k + 5)
    s.cancel(10, "meeting3")
    expect(s.last_booked(11, 2), ["meeting2", "meeting1"])
    expect(s.last_booked(12, 9), ["meeting2", "meeting1"])
    expect(s.last_booked(13, 0), [])


@case("busiest_rooms ranks rooms by total booked time")
def busiest_basic(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.add_room(2, "B")
    s.book_room(3, "A", 0, 30)
    s.book_room(4, "B", 0, 45)
    s.book_room(5, "A", 100, 120)
    expect(s.busiest_rooms(6, 2), ["A(50)", "B(45)"])


@case("rooms with nothing booked appear with 0, and ties go by room id")
def busiest_ties(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "b")
    s.add_room(2, "C")
    s.add_room(3, "A")
    s.book_room(4, "b", 0, 10)
    expect(s.busiest_rooms(5, 3), ["b(10)", "A(0)", "C(0)"])
