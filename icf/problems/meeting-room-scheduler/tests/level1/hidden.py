"""Level 1 — rooms and bookings (hidden cases)."""
import random

from icf_testkit import case, expect


class Model:
    """A deliberately naive reference: one flat list of meetings, rescanned every time."""

    def __init__(self):
        self.rooms = []          # room ids in the order they were added
        self.meetings = []       # dicts, in booking order; cancelled ones stay, flagged
        self.count = 0

    def _clash(self, room, start, end, skip=None):
        return any(m["active"] and m["room"] == room and m is not skip
                   and m["start"] < end and start < m["end"] for m in self.meetings)

    def _get(self, meeting_id):
        for m in self.meetings:
            if m["id"] == meeting_id and m["active"]:
                return m
        return None

    def _new(self, room, start, end):
        self.count += 1
        self.meetings.append({"id": f"meeting{self.count}", "room": room,
                              "start": start, "end": end, "active": True})
        return f"meeting{self.count}"

    def add_room(self, ts, room):
        if room in self.rooms:
            return False
        self.rooms.append(room)
        return True

    def book_room(self, ts, room, start, end):
        if room not in self.rooms or self._clash(room, start, end):
            return None
        return self._new(room, start, end)

    def cancel(self, ts, meeting_id):
        m = self._get(meeting_id)
        if m is None:
            return False
        m["active"] = False
        return True

    def get_meeting(self, ts, meeting_id):
        m = self._get(meeting_id)
        return None if m is None else f"{m['room']}({m['start']}-{m['end']})"

    def free_rooms(self, ts, start, end):
        return [r for r in self.rooms if not self._clash(r, start, end)]

    def book_any(self, ts, start, end):
        free = self.free_rooms(ts, start, end)
        return None if not free else self._new(free[0], start, end)

    def last_booked(self, ts, n):
        return [m["id"] for m in reversed(self.meetings) if m["active"]][:n]

    def busiest_rooms(self, ts, n):
        used = {r: sum(m["end"] - m["start"] for m in self.meetings
                       if m["active"] and m["room"] == r) for r in self.rooms}
        return [f"{r}({used[r]})" for r in sorted(self.rooms, key=lambda r: (-used[r], r))][:n]

    def reschedule(self, ts, meeting_id, start, end):
        m = self._get(meeting_id)
        if m is None or self._clash(m["room"], start, end, skip=m):
            return False
        m["start"], m["end"] = start, end
        return True

    def close_room(self, ts, room):
        if room not in self.rooms:
            return None
        self.rooms.remove(room)
        mine = [m for m in self.meetings if m["active"] and m["room"] == room]
        mine.sort(key=lambda m: m["start"])
        cancelled = []
        for m in mine:
            m["room"] = None
            target = next((r for r in self.rooms if not self._clash(r, m["start"], m["end"])), None)
            if target is None:
                m["active"] = False
                cancelled.append(m["id"])
            else:
                m["room"] = target
        return cancelled


def workload(seed, steps, ops, n_rooms=4, span=200, longest=60):
    """A random call sequence using only `ops`; timestamps strictly increase."""
    rng = random.Random(seed)
    names = ["Alpha", "Beta", "Gamma", "Delta", "Omega", "Z1"][:n_rooms]
    calls = []
    booked = 0
    for ts in range(1, steps + 1):
        op = rng.choice(ops)
        start = rng.randint(0, span)
        end = start + rng.randint(1, longest)
        some_meeting = f"meeting{rng.randint(1, booked + 2)}"
        if op in ("add_room", "close_room"):
            args = [ts, rng.choice(names)]
        elif op == "book_room":
            args = [ts, rng.choice(names), start, end]
            booked += 1
        elif op in ("book_any", "free_rooms"):
            args = [ts, start, end]
            booked += op == "book_any"
        elif op in ("cancel", "get_meeting"):
            args = [ts, some_meeting]
        elif op in ("last_booked", "busiest_rooms"):
            args = [ts, rng.randint(0, 6)]
        else:  # reschedule
            args = [ts, some_meeting, start, end]
        calls.append((op, args))
    return calls


def replay(scheduler, model, calls):
    """Run the same calls on the solver's scheduler and the model, comparing each result."""
    for name, args in calls:
        expect(getattr(scheduler, name)(*args), getattr(model, name)(*args),
               f"{name}{tuple(args)}")


@case("a refused add_room keeps the existing room's meetings")
def failed_add_is_inert(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    s.book_room(2, "Alpha", 0, 60)
    expect(s.add_room(3, "Alpha"), False)
    expect(s.book_room(4, "Alpha", 30, 90), None, "meeting1 still blocks the room")
    expect(s.get_meeting(5, "meeting1"), "Alpha(0-60)")


@case("failed bookings do not use up a meeting number")
def failed_bookings_no_number(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    s.book_room(2, "Alpha", 0, 60)
    s.book_room(3, "Alpha", 10, 20)
    s.book_room(4, "Nope", 10, 20)
    expect(s.book_room(5, "Alpha", 60, 61), "meeting2")


@case("meeting numbers are never reused after a cancel")
def numbers_not_reused(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Alpha")
    s.book_room(2, "Alpha", 0, 10)
    s.cancel(3, "meeting1")
    expect(s.book_room(4, "Alpha", 0, 10), "meeting2")
    expect(s.get_meeting(5, "meeting1"), None)
    expect(s.get_meeting(6, "meeting2"), "Alpha(0-10)")


@case("a meeting inside another, or around it, overlaps")
def containment_overlaps(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "R")
    expect(s.book_room(2, "R", 100, 200), "meeting1")
    expect(s.book_room(3, "R", 120, 140), None, "inside")
    expect(s.book_room(4, "R", 50, 250), None, "around")
    expect(s.book_room(5, "R", 100, 200), None, "identical")
    expect(s.book_room(6, "R", 199, 200), None, "the last minute")
    expect(s.book_room(7, "R", 50, 100), "meeting2", "ends as meeting1 starts")


@case("a one-minute meeting and a meeting at time 0 are fine")
def small_meetings(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "R")
    expect(s.book_room(2, "R", 0, 1), "meeting1")
    expect(s.book_room(3, "R", 1, 2), "meeting2")
    expect(s.get_meeting(4, "meeting1"), "R(0-1)")


@case("cancelling a meeting that was never booked returns False")
def cancel_unknown(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "R")
    expect(s.cancel(2, "meeting1"), False)
    expect(s.book_room(3, "R", 0, 5), "meeting1")
    expect(s.cancel(4, "Meeting1"), False, "ids are case-sensitive")


@case("a random workload of bookings and cancels matches a reference model")
def fuzz_level1(MeetingScheduler):
    for seed in (1, 2, 3):
        replay(MeetingScheduler(), Model(),
               workload(seed, 400, ["add_room", "book_room", "book_room", "book_room",
                                    "cancel", "get_meeting"]))
