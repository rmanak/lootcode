"""Level 1 — records and conditional writes (visible cases)."""
from icf_testkit import case, expect


@case("set then get returns the value")
def set_get(Database):
    db = Database()
    db.set(1, "user", "name", "Ada")
    expect(db.get(2, "user", "name"), "Ada")


@case("get of a missing record or field returns None")
def get_missing(Database):
    db = Database()
    db.set(1, "user", "name", "Ada")
    expect(db.get(2, "user", "email"), None)
    expect(db.get(3, "nobody", "name"), None)
    expect(db.get(4, "user", "name"), "Ada")


@case("set replaces an existing value")
def set_replaces(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    db.set(2, "k", "f", "b")
    expect(db.get(3, "k", "f"), "b")


@case("compare_and_set only writes when the expected value matches")
def cas(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    expect(db.compare_and_set(2, "k", "f", "x", "b"), False)
    expect(db.get(3, "k", "f"), "a", "a failed compare changes nothing")
    expect(db.compare_and_set(4, "k", "f", "a", "b"), True)
    expect(db.get(5, "k", "f"), "b")


@case("compare_and_delete only deletes when the expected value matches")
def cad(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    expect(db.compare_and_delete(2, "k", "f", "b"), False)
    expect(db.get(3, "k", "f"), "a")
    expect(db.compare_and_delete(4, "k", "f", "a"), True)
    expect(db.get(5, "k", "f"), None)
    expect(db.compare_and_delete(6, "k", "f", "a"), False, "already gone")
