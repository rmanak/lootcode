"""Level 2 — the busiest parcels (hidden cases)."""
import random

from icf_testkit import case, expect


@case("removed event types no longer count, and deleted parcels drop out")
def removal_counts(ParcelTracker):
    t = ParcelTracker()
    t.record_event("a", "x", 5)
    t.record_event("a", "y", 5)
    t.record_event("b", "x", 7)
    t.remove_event("a", "x")
    expect(t.top_parcels(3), ["b(7)", "a(5)"])
    t.remove_event("b", "x")
    expect(t.top_parcels(3), ["a(5)"])


@case("an empty tracker ranks nothing")
def empty(ParcelTracker):
    t = ParcelTracker()
    expect(t.top_parcels(3), [])
    t.record_event("z", "e", 1)
    expect(t.top_parcels(3), ["z(1)"])


@case("ids order as plain strings")
def string_order(ParcelTracker):
    t = ParcelTracker()
    for pid in ["p10", "p9", "P1"]:
        t.record_event(pid, "e", 1)
    expect(t.top_parcels(3), ["P1(1)", "p10(1)", "p9(1)"])


@case("a random run matches a reference model")
def random_model(ParcelTracker):
    rng = random.Random(3)
    t = ParcelTracker()
    model = {}
    for step in range(400):
        pid, ev = rng.choice("abcde"), rng.choice("xyz")
        if rng.random() < 0.75:
            count = rng.randint(1, 9)
            tally = model.setdefault(pid, {})
            tally[ev] = tally.get(ev, 0) + count
            expect(t.record_event(pid, ev, count), tally[ev])
        else:
            ok = ev in model.get(pid, {})
            expect(t.remove_event(pid, ev), ok)
            if ok:
                del model[pid][ev]
                if not model[pid]:
                    del model[pid]
        if step % 20 == 0:
            n = rng.randint(0, 6)
            want = sorted(model, key=lambda p: (-sum(model[p].values()), p))[:n]
            expect(t.top_parcels(n), [f"{p}({sum(model[p].values())})" for p in want])
