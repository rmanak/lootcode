"""Level 3 — fields that expire (hidden cases)."""
from icf_testkit import case, expect


@case("compare_and_set keeps the field's current lifetime")
def cas_keeps_lifetime(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "a", 10)        # expires at 11
    expect(db.compare_and_set(5, "k", "f", "a", "b"), True)
    expect(db.get(10, "k", "f"), "b")
    expect(db.get(11, "k", "f"), None, "still expires at 11")


@case("a plain set makes a field permanent again")
def set_removes_ttl(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "a", 5)
    db.set(2, "k", "f", "b")
    expect(db.get(1000, "k", "f"), "b")


@case("set_with_ttl on a live field restarts the countdown")
def ttl_restart(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "a", 5)         # expires at 6
    db.set_with_ttl(4, "k", "f", "b", 2)         # now expires at 6 too
    expect(db.get(5, "k", "f"), "b")
    expect(db.get(6, "k", "f"), None)
    db.set_with_ttl(7, "k", "f", "c", 100)
    db.set_with_ttl(8, "k", "f", "d", 1)         # shorter than before
    expect(db.get(9, "k", "f"), None)


@case("a ttl of 0 is already expired")
def ttl_zero(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    db.set_with_ttl(2, "k", "f", "b", 0)
    expect(db.get(2 + 1, "k", "f"), None)
    expect(db.scan(4, "k"), [])
    db.set(5, "k", "g", "x")
    expect(db.scan(6, "k"), ["g(x)"])


@case("compare_and_set_with_ttl can shorten a permanent field's life")
def cas_ttl_on_permanent(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    expect(db.compare_and_set_with_ttl(2, "k", "f", "a", "b", 3), True)
    expect(db.scan_by_prefix(4, "k", "f"), ["f(b)"])
    expect(db.scan_by_prefix(5, "k", "f"), [])


@case("compare_and_delete removes a live field that has a TTL")
def cad_ttl(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "a", 50)
    expect(db.compare_and_delete(2, "k", "f", "a"), True)
    expect(db.get(3, "k", "f"), None)
    expect(db.compare_and_set_with_ttl(4, "k", "f", "a", "b", 5), False)


@case("expiry is judged at the time of the read, not the write")
def judged_at_read(Database):
    db = Database()
    db.set_with_ttl(10, "k", "f", "a", 10)
    expect(db.get(19, "k", "f"), "a")
    expect(db.scan(20, "k"), [])
