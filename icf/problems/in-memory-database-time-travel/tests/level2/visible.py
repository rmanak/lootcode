"""Level 2 — scanning a record (visible cases)."""
from icf_testkit import case, expect


@case("scan lists every field sorted by name")
def scan_sorted(Database):
    db = Database()
    db.set(1, "cfg", "port", "80")
    db.set(2, "cfg", "host", "x")
    db.set(3, "cfg", "mode", "fast")
    expect(db.scan(4, "cfg"), ["host(x)", "mode(fast)", "port(80)"])


@case("scan of a missing record is an empty list")
def scan_missing(Database):
    db = Database()
    db.set(1, "cfg", "a", "1")
    expect(db.scan(2, "other"), [])
    expect(db.scan(3, "cfg"), ["a(1)"])


@case("scan_by_prefix keeps only matching fields")
def prefix(Database):
    db = Database()
    db.set(1, "cfg", "db_host", "h")
    db.set(2, "cfg", "db_port", "1")
    db.set(3, "cfg", "cache", "on")
    expect(db.scan_by_prefix(4, "cfg", "db_"), ["db_host(h)", "db_port(1)"])
    expect(db.scan_by_prefix(5, "cfg", "zz"), [])
