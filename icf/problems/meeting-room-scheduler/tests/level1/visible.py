"""Level 1 — rooms and bookings (visible cases)."""
from icf_testkit import case, expect

@case("a room is added once, and the second attempt with the same id is refused")
def add_room_once(MeetingScheduler):
    s = MeetingScheduler()
    expect(s.add_room(1, "Alpha"), True)
    expect(s.add_room(2, "Alpha"), False)


@case("booking returns meeting ids numbered from 1")
def booking_ids(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    expect(s.book_room(2, "Alpha", 0, 30), "meeting1")
    expect(s.book_room(3, "Alpha", 30, 60), "meeting2")


@case("a meeting that overlaps another in the same room is refused")
def overlap_refused(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    expect(s.book_room(2, "Alpha", 600, 660), "meeting1")
    expect(s.book_room(3, "Alpha", 630, 700), None)
    expect(s.book_room(4, "Alpha", 500, 601), None)
    expect(s.book_room(5, "Alpha", 660, 720), "meeting2", "touching at 660 is not an overlap")


@case("booking a room that does not exist is refused")
def unknown_room(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    expect(s.book_room(2, "Beta", 0, 10), None)
    expect(s.book_room(3, "Alpha", 0, 10), "meeting1")


@case("meetings in different rooms never conflict")
def rooms_independent(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    s.add_room(2, "Beta")
    expect(s.book_room(3, "Alpha", 0, 100), "meeting1")
    expect(s.book_room(4, "Beta", 0, 100), "meeting2")


@case("get_meeting describes a meeting as room(start-end)")
def get_meeting_format(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    s.book_room(2, "Alpha", 600, 660)
    expect(s.get_meeting(3, "meeting1"), "Alpha(600-660)")
    expect(s.get_meeting(4, "meeting2"), None, "no such meeting")


@case("cancel frees the time, and a cancelled meeting is gone")
def cancel_frees(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    s.book_room(2, "Alpha", 0, 60)
    expect(s.cancel(3, "meeting1"), True)
    expect(s.cancel(4, "meeting1"), False)
    expect(s.get_meeting(5, "meeting1"), None)
    expect(s.book_room(6, "Alpha", 0, 60), "meeting2")
