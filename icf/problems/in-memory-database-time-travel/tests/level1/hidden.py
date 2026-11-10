"""Level 1 — records and conditional writes (hidden cases)."""
import random

from icf_testkit import case, expect


@case("compare_and_set never creates a field or record")
def cas_does_not_create(Database):
    db = Database()
    expect(db.compare_and_set(1, "k", "f", "", "v"), False)
    db.set(2, "k", "other", "x")
    expect(db.compare_and_set(3, "k", "f", "", "v"), False)
    expect(db.get(4, "k", "f"), None)
    expect(db.get(5, "k", "other"), "x")


@case("the empty string is a value that can be matched")
def empty_string_value(Database):
    db = Database()
    db.set(1, "k", "f", "")
    expect(db.get(2, "k", "f"), "")
    expect(db.compare_and_set(3, "k", "f", "", "full"), True)
    expect(db.get(4, "k", "f"), "full")
    db.set(5, "k", "g", "")
    expect(db.compare_and_delete(6, "k", "g", ""), True)
    expect(db.get(7, "k", "g"), None)


@case("matching is case-sensitive")
def case_sensitive(Database):
    db = Database()
    db.set(1, "k", "f", "Yes")
    expect(db.compare_and_set(2, "k", "f", "yes", "no"), False)
    expect(db.compare_and_delete(3, "k", "f", "YES"), False)
    expect(db.get(4, "k", "f"), "Yes")


@case("a compare that writes the same value still succeeds")
def cas_same_value(Database):
    db = Database()
    db.set(1, "k", "f", "v")
    expect(db.compare_and_set(2, "k", "f", "v", "v"), True)
    expect(db.get(3, "k", "f"), "v")


@case("a deleted field can be set again")
def set_after_delete(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    db.compare_and_delete(2, "k", "f", "a")
    db.set(3, "k", "f", "b")
    expect(db.get(4, "k", "f"), "b")


@case("records and fields are independent")
def independent(Database):
    db = Database()
    db.set(1, "a", "f", "1")
    db.set(2, "b", "f", "2")
    db.set(3, "a", "g", "3")
    db.compare_and_delete(4, "a", "f", "1")
    expect(db.get(5, "b", "f"), "2")
    expect(db.get(6, "a", "g"), "3")
    expect(db.get(7, "a", "f"), None)


@case("a random sequence matches a dictionary")
def random_model(Database):
    rng = random.Random(7)
    db = Database()
    model = {}
    for ts in range(1, 400):
        key, field = rng.choice("ab"), rng.choice("xyz")
        value = rng.choice(["", "1", "2"])
        op = rng.random()
        if op < 0.35:
            db.set(ts, key, field, value)
            model[(key, field)] = value
        elif op < 0.6:
            new = rng.choice(["1", "2", "3"])
            ok = model.get((key, field)) == value
            expect(db.compare_and_set(ts, key, field, value, new), ok)
            if ok:
                model[(key, field)] = new
        elif op < 0.8:
            ok = model.get((key, field)) == value
            expect(db.compare_and_delete(ts, key, field, value), ok)
            if ok:
                del model[(key, field)]
        else:
            expect(db.get(ts, key, field), model.get((key, field)), f"at {ts}")
