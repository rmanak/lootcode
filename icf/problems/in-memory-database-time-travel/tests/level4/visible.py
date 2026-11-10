"""Level 4 — reading the past (visible cases)."""
from icf_testkit import case, expect


@case("get_when returns the value a field held at an earlier moment")
def basic(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    db.set(5, "k", "f", "b")
    expect(db.get_when(10, "k", "f", 1), "a")
    expect(db.get_when(11, "k", "f", 4), "a")
    expect(db.get_when(12, "k", "f", 5), "b", "the write at at_timestamp counts")


@case("before the first write, the field had no value")
def before_first_write(Database):
    db = Database()
    db.set(3, "k", "f", "a")
    expect(db.get_when(4, "k", "f", 2), None)
    expect(db.get_when(5, "k", "g", 4), None)
    expect(db.get_when(6, "x", "f", 4), None)
    expect(db.get_when(7, "k", "f", 3), "a")


@case("a delete hides the value from then on, without falling back")
def delete_in_past(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    db.set(2, "k", "f", "b")
    db.compare_and_delete(3, "k", "f", "b")
    expect(db.get_when(9, "k", "f", 2), "b")
    expect(db.get_when(9 + 1, "k", "f", 3), None, "not the older 'a'")


@case("a TTL is judged as of at_timestamp")
def ttl_in_past(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "a", 5)      # alive on [1, 6)
    expect(db.get_when(20, "k", "f", 5), "a")
    expect(db.get_when(21, "k", "f", 6), None)
