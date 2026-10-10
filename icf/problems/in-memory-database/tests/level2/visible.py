"""Level 2 — scanning a record (visible cases)."""
from icf_testkit import case, expect


@case("scan lists every field, sorted by field name")
def scan_sorted(Database):
    db = Database()
    db.set(1, "cfg", "region", "eu-west")
    db.set(2, "cfg", "db_host", "10.0.0.4")
    db.set(3, "cfg", "db_port", "5432")
    expect(db.scan(4, "cfg"), "db_host(10.0.0.4), db_port(5432), region(eu-west)")


@case("scan returns the empty string for a missing or emptied record")
def scan_empty(Database):
    db = Database()
    expect(db.scan(1, "nope"), "")
    db.set(2, "cfg", "only", "v")
    db.delete(3, "cfg", "only")
    expect(db.scan(4, "cfg"), "", "every field has been deleted")


@case("scan_by_prefix keeps only the fields whose name starts with the prefix")
def scan_prefix(Database):
    db = Database()
    db.set(1, "cfg", "db_host", "10.0.0.4")
    db.set(2, "cfg", "db_port", "5432")
    db.set(3, "cfg", "region", "eu-west")
    expect(db.scan_by_prefix(4, "cfg", "db_"), "db_host(10.0.0.4), db_port(5432)")


@case("a prefix that matches nothing gives the empty string")
def scan_prefix_no_match(Database):
    db = Database()
    db.set(1, "cfg", "region", "eu-west")
    expect(db.scan_by_prefix(2, "cfg", "cache"), "")
    expect(db.scan_by_prefix(3, "missing", "re"), "")


@case("the empty prefix matches every field")
def scan_prefix_empty(Database):
    db = Database()
    db.set(1, "cfg", "a", "1")
    db.set(2, "cfg", "b", "2")
    expect(db.scan_by_prefix(3, "cfg", ""), db.scan(4, "cfg"))
    expect(db.scan_by_prefix(5, "cfg", ""), "a(1), b(2)")


@case("values are copied verbatim, and ordering is plain lexicographic")
def formatting_is_literal(Database):
    db = Database()
    db.set(1, "k", "Zebra", "last?")
    db.set(2, "k", "apple", "x(y), z")
    db.set(3, "k", "Ant", "")
    # Capitals sort before lower case; the value's own parentheses and comma
    # are not escaped or re-ordered.
    expect(db.scan(4, "k"), "Ant(), Zebra(last?), apple(x(y), z)")
