"""Level 3 — couriers (visible cases)."""
from icf_testkit import case, expect


@case("a courier can be assigned to an existing parcel")
def assign(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "scanned", 1)
    expect(t.assign_courier("p1", "c1"), True)
    expect(t.get_courier_parcels("c1"), ["p1"])
    expect(t.assign_courier("p9", "c1"), False, "no such parcel")


@case("assigning another courier replaces the first")
def reassign(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "scanned", 1)
    t.assign_courier("p1", "c1")
    expect(t.assign_courier("p1", "c1"), False, "already this courier")
    expect(t.assign_courier("p1", "c2"), True)
    expect(t.get_courier_parcels("c1"), [])
    expect(t.get_courier_parcels("c2"), ["p1"])


@case("only the assigned courier can record events")
def courier_events(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p1", "scanned", 1)
    t.assign_courier("p1", "c1")
    expect(t.record_courier_event("c1", "p1", "scanned", 2), 3)
    expect(t.record_courier_event("c2", "p1", "scanned", 2), None)
    expect(t.get_event_count("p1", "scanned"), 3)


@case("a courier's parcels are listed in id order")
def listing(ParcelTracker):
    t = ParcelTracker()
    for pid in ["p3", "p1", "p2"]:
        t.record_event(pid, "e", 1)
        t.assign_courier(pid, "c")
    expect(t.get_courier_parcels("c"), ["p1", "p2", "p3"])
    expect(t.get_courier_parcels("nobody"), [])
