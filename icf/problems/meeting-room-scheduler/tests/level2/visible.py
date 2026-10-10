"""Level 2 — finding a free room (visible cases)."""
from icf_testkit import case, expect

@case("free_rooms lists the rooms with nothing booked in the time, in added order")
def free_rooms_basic(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Gamma")
    s.add_room(2, "Alpha")
    s.add_room(3, "Beta")
    s.book_room(4, "Alpha", 0, 60)
    expect(s.free_rooms(5, 30, 90), ["Gamma", "Beta"])
    expect(s.free_rooms(6, 60, 90), ["Gamma", "Alpha", "Beta"], "a meeting ending at 60 does not block 60")


@case("book_any takes the first free room in the order the rooms were added")
def book_any_first(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Beta")
    s.add_room(2, "Alpha")
    expect(s.book_any(3, 0, 60), "meeting1")
    expect(s.get_meeting(4, "meeting1"), "Beta(0-60)")
    expect(s.book_any(5, 30, 90), "meeting2")
    expect(s.get_meeting(6, "meeting2"), "Alpha(30-90)")


@case("book_any returns None when every room is busy")
def book_any_none(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_any(2, 0, 100)
    expect(s.book_any(3, 50, 60), None)
    expect(s.free_rooms(4, 50, 60), [])
    expect(s.book_any(5, 100, 110), "meeting2")


@case("a meeting booked with book_any can be cancelled like any other")
def book_any_cancel(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_any(2, 0, 100)
    expect(s.cancel(3, "meeting1"), True)
    expect(s.free_rooms(4, 0, 100), ["A"])
