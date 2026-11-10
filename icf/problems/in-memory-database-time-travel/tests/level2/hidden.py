"""Level 2 — scanning a record (hidden cases)."""
from icf_testkit import case, expect


@case("deleted fields are not listed, and an emptied record scans as []")
def deleted_not_listed(Database):
    db = Database()
    db.set(1, "k", "a", "1")
    db.set(2, "k", "b", "2")
    db.compare_and_delete(3, "k", "a", "1")
    expect(db.scan(4, "k"), ["b(2)"])
    db.compare_and_delete(5, "k", "b", "2")
    expect(db.scan(6, "k"), [])
    db.set(7, "k", "c", "3")
    expect(db.scan(8, "k"), ["c(3)"])


@case("sorting is plain string order")
def string_order(Database):
    db = Database()
    for ts, name in enumerate(["b", "B", "10", "9", "a"], start=1):
        db.set(ts, "k", name, "v")
    expect(db.scan(10, "k"), ["10(v)", "9(v)", "B(v)", "a(v)", "b(v)"])


@case("the empty prefix matches everything; a whole name matches itself")
def prefix_edges(Database):
    db = Database()
    db.set(1, "k", "ab", "1")
    db.set(2, "k", "abc", "2")
    db.set(3, "k", "b", "3")
    expect(db.scan_by_prefix(4, "k", ""), ["ab(1)", "abc(2)", "b(3)"])
    expect(db.scan_by_prefix(5, "k", "ab"), ["ab(1)", "abc(2)"])
    expect(db.scan_by_prefix(6, "k", "abc"), ["abc(2)"])
    expect(db.scan_by_prefix(7, "k", "B"), [], "prefixes are case-sensitive")


@case("empty values are listed with empty parentheses")
def empty_values(Database):
    db = Database()
    db.set(1, "k", "f", "")
    expect(db.scan(2, "k"), ["f()"])


@case("scans show the latest value after compare_and_set")
def scan_after_cas(Database):
    db = Database()
    db.set(1, "k", "f", "old")
    db.compare_and_set(2, "k", "f", "old", "new")
    expect(db.scan(3, "k"), ["f(new)"])
