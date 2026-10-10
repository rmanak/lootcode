"""Level 3 — recent bookings and busy rooms (hidden cases)."""
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


@case("an empty scheduler has no recent bookings and no ranking")
def empty(MeetingScheduler):
    s = MeetingScheduler()
    expect(s.last_booked(1, 3), [])
    expect(s.busiest_rooms(2, 3), [])
    s.add_room(3, "A")
    expect(s.busiest_rooms(4, 3), ["A(0)"])


@case("a cancelled meeting stops counting towards its room's booked time")
def cancel_reduces_time(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.add_room(2, "B")
    s.book_room(3, "A", 0, 100)
    s.book_room(4, "B", 0, 60)
    s.cancel(5, "meeting1")
    expect(s.busiest_rooms(6, 2), ["B(60)", "A(0)"])


@case("tie-breaking uses ordinary string order, not the order rooms were added")
def busiest_string_order(MeetingScheduler):
    s = MeetingScheduler()
    for i, r in enumerate(["R10", "R2", "Ra", "RA"], start=1):
        s.add_room(i, r)
    expect(s.busiest_rooms(10, 4), ["R10(0)", "R2(0)", "RA(0)", "Ra(0)"])
    expect(s.busiest_rooms(11, 1), ["R10(0)"])


@case("meetings booked with book_any count towards the room they were given")
def book_any_counts(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "B")
    s.add_room(2, "A")
    s.book_any(3, 0, 40)
    s.book_any(4, 20, 30)
    expect(s.busiest_rooms(5, 2), ["B(40)", "A(10)"])
    expect(s.last_booked(6, 5), ["meeting2", "meeting1"])


@case("last_booked reaches past many cancelled meetings")
def last_booked_deep(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    for k in range(1, 51):
        s.book_room(1 + k, "A", k * 10, k * 10 + 5)
    for k in range(10, 51):
        s.cancel(100 + k, f"meeting{k}")
    expect(s.last_booked(200, 3), ["meeting9", "meeting8", "meeting7"])


@case("a random workload with rankings matches a reference model")
def fuzz_level3(MeetingScheduler):
    for seed in (21, 22, 23):
        replay(MeetingScheduler(), Model(),
               workload(seed, 400, ["add_room", "book_room", "book_any", "book_any",
                                    "cancel", "get_meeting", "free_rooms",
                                    "last_booked", "busiest_rooms"]))
