"""Level 1 — recording events (visible cases)."""
from icf_testkit import case, expect


@case("record_event returns the running total for that event type")
def running_total(ParcelTracker):
    t = ParcelTracker()
    expect(t.record_event("p1", "scanned", 2), 2)
    expect(t.record_event("p1", "scanned", 3), 5)
    expect(t.record_event("p1", "delayed", 1), 1, "each event type has its own tally")


@case("get_event_count reads a tally, or None")
def get_count(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "scanned", 4)
    expect(t.get_event_count("p1", "scanned"), 4)
    expect(t.get_event_count("p1", "lost"), None)
    expect(t.get_event_count("p2", "scanned"), None)


@case("remove_event removes one event type")
def remove(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "scanned", 4)
    t.record_event("p1", "delayed", 1)
    expect(t.remove_event("p1", "scanned"), True)
    expect(t.get_event_count("p1", "scanned"), None)
    expect(t.get_event_count("p1", "delayed"), 1)
    expect(t.remove_event("p1", "scanned"), False, "already removed")
