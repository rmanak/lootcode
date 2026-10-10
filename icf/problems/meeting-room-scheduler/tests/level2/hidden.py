"""Level 2 — finding a free room (hidden cases)."""
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


@case("free_rooms and book_any with no rooms at all")
def no_rooms(MeetingScheduler):
    s = MeetingScheduler()
    expect(s.free_rooms(1, 0, 10), [])
    expect(s.book_any(2, 0, 10), None)
    s.add_room(3, "A")
    expect(s.book_any(4, 0, 10), "meeting1", "the failed book_any used no number")


@case("book_any and book_room share one sequence of meeting numbers")
def shared_numbering(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.add_room(2, "B")
    expect(s.book_room(3, "B", 0, 10), "meeting1")
    expect(s.book_any(4, 0, 10), "meeting2")
    expect(s.book_room(5, "A", 20, 30), "meeting3")
    expect(s.get_meeting(6, "meeting2"), "A(0-10)")


@case("a room added later is used only after the earlier rooms")
def later_room(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "Z")
    s.book_any(2, 0, 10)
    s.add_room(3, "A")
    expect(s.book_any(4, 20, 30), "meeting2")
    expect(s.get_meeting(5, "meeting2"), "Z(20-30)", "Z is still first and free")
    expect(s.book_any(6, 5, 15), "meeting3")
    expect(s.get_meeting(7, "meeting3"), "A(5-15)")


@case("a cancelled meeting no longer makes a room busy")
def cancelled_not_busy(MeetingScheduler):
    s = MeetingScheduler()
    s.add_room(1, "A")
    s.add_room(2, "B")
    s.book_room(3, "A", 0, 50)
    s.cancel(4, "meeting1")
    expect(s.free_rooms(5, 10, 20), ["A", "B"])
    expect(s.book_any(6, 10, 20), "meeting2")
    expect(s.get_meeting(7, "meeting2"), "A(10-20)")


@case("book_any fills rooms as meetings pile up at the same time")
def pile_up(MeetingScheduler):
    s = MeetingScheduler()
    for i, r in enumerate(["R1", "R2", "R3"], start=1):
        s.add_room(i, r)
    got = [s.book_any(10 + k, 100, 200) for k in range(4)]
    expect(got, ["meeting1", "meeting2", "meeting3", None])
    expect([s.get_meeting(20 + k, f"meeting{k}") for k in (1, 2, 3)],
           ["R1(100-200)", "R2(100-200)", "R3(100-200)"])


@case("a random workload with free_rooms and book_any matches a reference model")
def fuzz_level2(MeetingScheduler):
    for seed in (11, 12, 13):
        replay(MeetingScheduler(), Model(),
               workload(seed, 400, ["add_room", "book_room", "book_any", "book_any",
                                    "cancel", "get_meeting", "free_rooms"]))
