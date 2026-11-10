"""Level 3 — couriers (hidden cases)."""
from icf_testkit import case, expect


@case("courier events count in the parcel ranking")
def courier_events_rank(ParcelTracker):
    t = ParcelTracker()
    t.record_event("a", "e", 1)
    t.record_event("b", "e", 2)
    t.assign_courier("a", "c")
    t.record_courier_event("c", "a", "delivered", 5)
    expect(t.top_parcels(2), ["a(6)", "b(2)"])


@case("a courier cannot record on a parcel that does not exist")
def courier_unknown_parcel(ParcelTracker):
    t = ParcelTracker()
    expect(t.record_courier_event("c", "p", "e", 1), None)
    expect(t.get_event_count("p", "e"), None, "and the parcel is not created")
    t.record_event("p", "e", 1)
    expect(t.record_courier_event("c", "p", "e", 1), None, "not assigned")
    t.assign_courier("p", "c")
    expect(t.record_courier_event("c", "p", "e", 1), 2)


@case("a parcel deleted by remove_event loses its courier")
def deleted_parcel_loses_courier(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "e", 1)
    t.assign_courier("p", "c")
    t.remove_event("p", "e")
    expect(t.get_courier_parcels("c"), [])
    t.record_event("p", "e", 1)
    expect(t.get_courier_parcels("c"), [], "the new parcel has no courier")
    expect(t.assign_courier("p", "c"), True)


@case("removing one of several event types keeps the courier")
def partial_remove_keeps_courier(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "a", 1)
    t.record_event("p", "b", 1)
    t.assign_courier("p", "c")
    t.remove_event("p", "a")
    expect(t.get_courier_parcels("c"), ["p"])


@case("a courier can carry many parcels and lose some to others")
def many_parcels(ParcelTracker):
    t = ParcelTracker()
    for i in range(10):
        t.record_event(f"p{i}", "e", 1)
        t.assign_courier(f"p{i}", "c1")
    for i in range(0, 10, 3):
        t.assign_courier(f"p{i}", "c2")
    expect(t.get_courier_parcels("c2"), ["p0", "p3", "p6", "p9"])
    expect(t.get_courier_parcels("c1"), ["p1", "p2", "p4", "p5", "p7", "p8"])
