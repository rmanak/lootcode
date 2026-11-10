"""Level 4 — undo and sign-out (hidden cases)."""
from icf_testkit import case, expect


@case("undo on an unknown parcel, or one never assigned, returns False")
def undo_nothing(ParcelTracker):
    t = ParcelTracker()
    expect(t.undo_assignment("p"), False)
    t.record_event("p", "e", 1)
    expect(t.undo_assignment("p"), False)
    t.assign_courier("p", "c")
    expect(t.undo_assignment("p"), True)


@case("refused assignments are not changes and cannot be undone")
def refused_not_recorded(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "e", 1)
    t.assign_courier("p", "c1")
    t.assign_courier("p", "c1")             # refused
    expect(t.undo_assignment("p"), True)
    expect(t.undo_assignment("p"), False)


@case("a re-created parcel has no history to undo")
def recreated(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "e", 1)
    t.assign_courier("p", "c1")
    t.assign_courier("p", "c2")
    t.remove_event("p", "e")
    t.record_event("p", "e", 1)
    expect(t.undo_assignment("p"), False)


@case("after undoing a sign-out, the courier can record again")
def undo_then_record(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "e", 1)
    t.assign_courier("p", "c")
    t.sign_out("c")
    expect(t.record_courier_event("c", "p", "e", 1), None)
    t.undo_assignment("p")
    expect(t.record_courier_event("c", "p", "e", 1), 2)


@case("a long history unwinds in exact reverse order")
def long_history(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "e", 1)
    sequence = ["c1", "c2", "c1", "c3"]
    for courier in sequence:
        t.assign_courier("p", courier)
    t.sign_out("c3")                       # None after c3
    expect(t.get_courier_parcels("c3"), [])
    for expected in ["c3", "c1", "c2", "c1"]:
        expect(t.undo_assignment("p"), True)
        expect(t.get_courier_parcels(expected), ["p"], f"back to {expected}")
    expect(t.undo_assignment("p"), True)
    expect(t.undo_assignment("p"), False)


@case("signing out only touches that courier's parcels")
def sign_out_scope(ParcelTracker):
    t = ParcelTracker()
    for pid in ["a", "b"]:
        t.record_event(pid, "e", 1)
    t.assign_courier("a", "c1")
    t.assign_courier("b", "c2")
    t.sign_out("c1")
    expect(t.undo_assignment("b"), True, "b's own assignment")
    expect(t.undo_assignment("b"), False)
    expect(t.get_courier_parcels("c2"), [])


@case("a signed-out courier can be assigned again")
def reassign_after_sign_out(ParcelTracker):
    t = ParcelTracker()
    t.record_event("p", "e", 1)
    t.assign_courier("p", "c")
    t.sign_out("c")
    expect(t.assign_courier("p", "c"), True)
    expect(t.undo_assignment("p"), True)
    expect(t.get_courier_parcels("c"), [], "undo returns to the signed-out state")
