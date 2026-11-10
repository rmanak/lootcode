"""Level 4 — undo and sign-out (visible cases)."""
from icf_testkit import case, expect


@case("undo restores the previous courier")
def undo(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "e", 1)
    t.assign_courier("p", "c1")
    t.assign_courier("p", "c2")
    expect(t.undo_assignment("p"), True)
    expect(t.get_courier_parcels("c1"), ["p"])
    expect(t.undo_assignment("p"), True)
    expect(t.get_courier_parcels("c1"), [], "back to no courier")
    expect(t.undo_assignment("p"), False, "nothing left to undo")


@case("sign_out releases every parcel the courier carries")
def sign_out(ParcelTracker):
    t = ParcelTracker()
    for pid in ["a", "b", "c"]:
        t.record_event(pid, "e", 1)
    t.assign_courier("a", "c1")
    t.assign_courier("b", "c1")
    t.assign_courier("c", "c2")
    expect(t.sign_out("c1"), 2)
    expect(t.get_courier_parcels("c1"), [])
    expect(t.get_courier_parcels("c2"), ["c"])
    expect(t.sign_out("c1"), 0)


@case("a sign-out can be undone parcel by parcel")
def undo_sign_out(ParcelTracker):
    t = ParcelTracker()
    for pid in ["a", "b"]:
        t.record_event(pid, "e", 1)
        t.assign_courier(pid, "c1")
    t.sign_out("c1")
    expect(t.undo_assignment("a"), True)
    expect(t.get_courier_parcels("c1"), ["a"])
