"""Level 1 — recording events (hidden cases)."""
from icf_testkit import case, expect


@case("removing the last event type deletes the parcel; it can start again")
def last_event_deletes(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "scanned", 9)
    expect(t.remove_event("p1", "scanned"), True)
    expect(t.remove_event("p1", "scanned"), False)
    expect(t.record_event("p1", "scanned", 1), 1, "a fresh tally")


@case("remove on an unknown parcel or event type returns False")
def remove_unknown(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "a", 1)
    expect(t.remove_event("p2", "a"), False)
    expect(t.remove_event("p1", "b"), False)
    expect(t.get_event_count("p1", "a"), 1)


@case("parcels and event types are independent and case-sensitive")
def independent(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "Scan", 1)
    t.record_event("p1", "scan", 2)
    t.record_event("P1", "scan", 3)
    expect(t.get_event_count("p1", "Scan"), 1)
    expect(t.get_event_count("p1", "scan"), 2)
    expect(t.get_event_count("P1", "scan"), 3)


@case("many events accumulate exactly")
def many(ParcelTracker):
    t = ParcelTracker()
    total = 0
    for i in range(1, 300):
        total += i
        expect(t.record_event("p", "e", i), total)
