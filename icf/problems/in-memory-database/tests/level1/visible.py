"""Level 1 — records and fields (visible cases)."""
from icf_testkit import case, expect


@case("set then get returns the value that was written")
def set_then_get(Database):
    db = Database()
    db.set(1, "user:42", "name", "Ada")
    expect(db.get(2, "user:42", "name"), "Ada")


@case("get returns None for a missing record and for a missing field")
def get_missing(Database):
    db = Database()
    db.set(1, "user:42", "name", "Ada")
    expect(db.get(2, "user:42", "name"), "Ada", "the field that does exist")
    expect(db.get(3, "user:42", "email"), None, "field was never written")
    expect(db.get(4, "user:7", "name"), None, "record was never created")


@case("set overwrites the field it already wrote")
def set_overwrites(Database):
    db = Database()
    db.set(1, "cfg", "mode", "draft")
    db.set(2, "cfg", "mode", "live")
    expect(db.get(3, "cfg", "mode"), "live")


@case("delete removes the field and reports that it did")
def delete_removes(Database):
    db = Database()
    db.set(1, "cfg", "mode", "live")
    expect(db.delete(2, "cfg", "mode"), True)
    expect(db.get(3, "cfg", "mode"), None, "the field should be gone")
    expect(db.delete(4, "cfg", "mode"), False, "deleting it twice")


@case("delete reports False for a field or record that was never there")
def delete_missing(Database):
    db = Database()
    db.set(1, "cfg", "mode", "live")
    expect(db.delete(2, "cfg", "other"), False)
    expect(db.delete(3, "nope", "mode"), False)


@case("compare_and_set writes only when the current value matches")
def compare_and_set_match(Database):
    db = Database()
    db.set(1, "user:42", "role", "reader")
    expect(db.compare_and_set(2, "user:42", "role", "reader", "admin"), True)
    expect(db.get(3, "user:42", "role"), "admin")
    expect(db.compare_and_set(4, "user:42", "role", "reader", "owner"), False,
           "the value is 'admin' now, so this must not write")
    expect(db.get(5, "user:42", "role"), "admin")


@case("compare_and_set never creates a missing field or record")
def compare_and_set_creates_nothing(Database):
    db = Database()
    db.set(1, "user:42", "name", "Ada")
    expect(db.compare_and_set(2, "user:42", "role", "", "admin"), False)
    expect(db.get(3, "user:42", "role"), None, "no field should have appeared")
    expect(db.compare_and_set(4, "ghost", "role", "", "admin"), False)
    expect(db.get(5, "ghost", "role"), None, "no record should have appeared")


@case("records with the same field names stay independent")
def records_are_independent(Database):
    db = Database()
    db.set(1, "a", "shared", "one")
    db.set(2, "b", "shared", "two")
    db.delete(3, "a", "shared")
    expect(db.get(4, "a", "shared"), None)
    expect(db.get(5, "b", "shared"), "two", "deleting from 'a' must not touch 'b'")
