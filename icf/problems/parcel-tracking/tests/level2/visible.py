"""Level 2 — the busiest parcels (visible cases)."""
from icf_testkit import case, expect


@case("parcels rank by their total number of events")
def ranking(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "scanned", 2)
    t.record_event("p2", "scanned", 1)
    t.record_event("p2", "delayed", 4)
    t.record_event("p3", "scanned", 3)
    expect(t.top_parcels(2), ["p2(5)", "p3(3)"])


@case("ties go to the smaller id, and n may exceed the parcels")
def ties(ParcelTracker):
    t = ParcelTracker()
    t.record_event("b", "x", 2)
    t.record_event("a", "x", 2)
    expect(t.top_parcels(5), ["a(2)", "b(2)"])
    expect(t.top_parcels(0), [])
