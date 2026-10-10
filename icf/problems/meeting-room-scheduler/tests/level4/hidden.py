"""Level 4 — rescheduling and closing rooms (hidden cases)."""
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


@case("reschedule of a cancelled or unknown meeting is refused")
def reschedule_missing(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 0, 10)
    s.cancel(3, "meeting1")
    expect(s.reschedule(4, "meeting1", 20, 30), False)
    expect(s.reschedule(5, "meeting7", 20, 30), False)
    expect(s.book_room(6, "A", 20, 30), "meeting2")


@case("a rescheduled meeting keeps its place in last_booked and its new length counts")
def reschedule_keeps_order(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 0, 10)
    s.book_room(3, "A", 20, 30)
    s.reschedule(4, "meeting1", 100, 190)
    expect(s.last_booked(5, 2), ["meeting2", "meeting1"])
    expect(s.busiest_rooms(6, 1), ["A(100)"])


@case("rescheduling may touch a neighbour exactly at its edges")
def reschedule_touching(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 0, 10)
    s.book_room(3, "A", 50, 60)
    s.book_room(4, "A", 100, 110)
    expect(s.reschedule(5, "meeting2", 10, 100), True)
    expect(s.reschedule(6, "meeting2", 9, 100), False)
    expect(s.get_meeting(7, "meeting2"), "A(10-100)")


@case("close_room handles meetings in start order, not booking order")
def close_room_start_order(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 300, 400)
    s.book_room(3, "A", 0, 100)
    s.book_room(4, "A", 200, 250)
    expect(s.close_room(5, "A"), ["meeting2", "meeting3", "meeting1"])


@case("meetings from a closed room go to the first room, in added order, that is free")
def close_room_target_order(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Z")
    s.add_room(2, "A")
    s.add_room(3, "M")
    s.book_room(4, "M", 0, 100)
    s.book_room(5, "Z", 50, 60)
    expect(s.close_room(6, "M"), [])
    expect(s.get_meeting(7, "meeting1"), "A(0-100)")
    expect(s.busiest_rooms(8, 5), ["A(100)", "Z(10)"])


@case("a meeting moved by close_room keeps its id and its place in last_booked")
def close_room_keeps_identity(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.add_room(2, "B")
    s.book_room(3, "B", 0, 10)
    s.book_room(4, "A", 0, 10)
    s.book_room(5, "B", 20, 30)
    s.close_room(6, "B")
    expect(s.last_booked(7, 5), ["meeting3", "meeting2"], "meeting1 was cancelled")
    expect(s.get_meeting(8, "meeting1"), None, "A was busy at 0-10")
    expect(s.get_meeting(9, "meeting3"), "A(20-30)")
    expect(s.cancel(10, "meeting1"), False)
    expect(s.cancel(11, "meeting3"), True)


@case("a closed room's id can be added again as a new, empty room at the end")
def reopen_room(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.add_room(2, "B")
    s.book_room(3, "A", 0, 10)
    s.close_room(4, "A")
    expect(s.get_meeting(5, "meeting1"), "B(0-10)")
    expect(s.add_room(6, "A"), True)
    expect(s.free_rooms(7, 0, 10), ["A"])
    expect(s.free_rooms(8, 20, 30), ["B", "A"], "the new A comes after B")
    expect(s.book_room(9, "A", 0, 10), "meeting2")


@case("closing the only room cancels every meeting")
def close_only_room(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.book_room(2, "A", 50, 60)
    s.book_room(3, "A", 0, 10)
    expect(s.close_room(4, "A"), ["meeting2", "meeting1"])
    expect(s.last_booked(5, 5), [])
    expect(s.busiest_rooms(6, 5), [])


@case("a random workload with rescheduling and closing matches a reference model")
def fuzz_level4(MeetingScheduler):
    for seed in (31, 32, 33, 34):
        replay(MeetingScheduler(), Model(),
               workload(seed, 500, ["add_room", "add_room", "book_room", "book_any",
                                    "book_any", "cancel", "get_meeting", "free_rooms",
                                    "last_booked", "busiest_rooms", "reschedule",
                                    "reschedule", "close_room"], n_rooms=5))
