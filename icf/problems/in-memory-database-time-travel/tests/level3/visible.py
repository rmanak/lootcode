"""Level 3 — fields that expire (visible cases)."""
from icf_testkit import case, expect


@case("a field is alive on [timestamp, timestamp + ttl)")
def ttl_window(Database):
    db = Database()
    db.set_with_ttl(1, "s", "token", "abc", 9)
    expect(db.get(9, "s", "token"), "abc")
    expect(db.get(10, "s", "token"), None, "expired at exactly 1 + 9")


@case("scans skip expired fields")
def scan_skips_expired(Database):
    db = Database()
    db.set_with_ttl(1, "s", "a", "1", 5)
    db.set(2, "s", "b", "2")
    expect(db.scan(3, "s"), ["a(1)", "b(2)"])
    expect(db.scan(6, "s"), ["b(2)"])


@case("compare_and_set_with_ttl writes the value and a new lifetime")
def cas_ttl(Database):
    db = Database()
    db.set(1, "s", "f", "a")
    expect(db.compare_and_set_with_ttl(2, "s", "f", "x", "b", 10), False)
    expect(db.compare_and_set_with_ttl(3, "s", "f", "a", "b", 10), True)
    expect(db.get(12, "s", "f"), "b")
    expect(db.get(13, "s", "f"), None)


@case("expired fields cannot be compared")
def expired_cannot_compare(Database):
    db = Database()
    db.set_with_ttl(1, "s", "f", "a", 2)
    expect(db.compare_and_set(3, "s", "f", "a", "b"), False)
    expect(db.compare_and_delete(4, "s", "f", "a"), False)
    db.set(5, "s", "f", "c")
    expect(db.get(6, "s", "f"), "c", "an expired field can be written again")
