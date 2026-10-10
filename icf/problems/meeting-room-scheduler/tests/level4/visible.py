"""Level 4 — rescheduling and closing rooms (visible cases)."""
from icf_testkit import case, expect

@case("reschedule moves a meeting to a free time in the same room")
def reschedule_basic(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 0, 60)
    expect(s.reschedule(3, "meeting1", 100, 130), True)
    expect(s.get_meeting(4, "meeting1"), "A(100-130)")
    expect(s.book_room(5, "A", 0, 60), "meeting2", "the old time is free")


@case("reschedule is refused if the new time overlaps another meeting in the room")
def reschedule_conflict(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 0, 60)
    s.book_room(3, "A", 60, 120)
    expect(s.reschedule(4, "meeting1", 30, 90), False)
    expect(s.get_meeting(5, "meeting1"), "A(0-60)", "nothing changed")


@case("a meeting may be moved over its own old time")
def reschedule_over_itself(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 0, 60)
    expect(s.reschedule(3, "meeting1", 30, 90), True)
    expect(s.get_meeting(4, "meeting1"), "A(30-90)")


@case("close_room moves meetings to the first free room and cancels the rest")
def close_room_basic(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.add_room(2, "B")
    s.add_room(3, "C")
    s.book_room(4, "A", 0, 60)
    s.book_room(5, "A", 100, 160)
    s.book_room(6, "B", 0, 60)
    s.book_room(7, "C", 0, 60)
    expect(s.close_room(8, "A"), ["meeting1"])
    expect(s.get_meeting(9, "meeting1"), None)
    expect(s.get_meeting(10, "meeting2"), "B(100-160)")


@case("close_room on a room that does not exist returns None")
def close_unknown(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    expect(s.close_room(2, "B"), None)
    expect(s.close_room(3, "A"), [])
    expect(s.close_room(4, "A"), None, "already closed")
