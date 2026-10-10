"""Level 2 — scanning a record (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a deleted field disappears from both scans")
def deleted_not_scanned(Database):
    db = Database()
    db.set(1, "k", "aa", "1")
    db.set(2, "k", "ab", "2")
    db.delete(3, "k", "aa")
    expect(db.scan(4, "k"), "ab(2)")
    expect(db.scan_by_prefix(5, "k", "a"), "ab(2)")


@case("scan shows the latest value, including after compare_and_set")
def scan_shows_latest(Database):
    db = Database()
    db.set(1, "k", "f", "old")
    db.set(2, "k", "f", "new")
    db.compare_and_set(3, "k", "f", "new", "newest")
    expect(db.scan(4, "k"), "f(newest)")


@case("field names sort as strings, not as numbers")
def sorting_is_lexicographic(Database):
    db = Database()
    for name in ("f10", "f9", "f100", "f1"):
        db.set(1, "k", name, name[1:])
    expect(db.scan(2, "k"), "f1(1), f10(10), f100(100), f9(9)")


@case("a scan reads one record and never another")
def scan_is_per_record(Database):
    db = Database()
    db.set(1, "a", "x", "1")
    db.set(2, "b", "y", "2")
    expect(db.scan(3, "a"), "x(1)")
    expect(db.scan_by_prefix(4, "b", ""), "y(2)")


@case("a prefix equal to a whole field name matches that field")
def prefix_is_whole_name(Database):
    db = Database()
    db.set(1, "k", "token", "t")
    db.set(2, "k", "token_expiry", "e")
    expect(db.scan_by_prefix(3, "k", "token"), "token(t), token_expiry(e)")
    expect(db.scan_by_prefix(4, "k", "token_"), "token_expiry(e)")


@case("scans agree with a reference model over a random workload")
def fuzz_scans(Database):
    def model_scan(state, prefix=""):
        return ", ".join(f"{f}({v})" for f, v in sorted(state.items())
                         if f.startswith(prefix))

    db = Database()
    state = {}
    rng = random.Random(4242)
    names = ["alpha", "alpine", "beta", "be", "gamma", "g", "Alpha"]
    for ts in range(1, 400):
        field = rng.choice(names)
        roll = rng.random()
        if roll < 0.55:
            value = f"v{rng.randrange(9)}"
            db.set(ts, "rec", field, value)
            state[field] = value
        elif roll < 0.7:
            db.delete(ts, "rec", field)
            state.pop(field, None)
        elif roll < 0.85:
            expect(db.scan(ts, "rec"), model_scan(state), f"scan at ts={ts}")
        else:
            prefix = rng.choice(["", "a", "al", "be", "g", "z", "Al"])
            expect(db.scan_by_prefix(ts, "rec", prefix), model_scan(state, prefix),
                   f"scan_by_prefix({prefix!r}) at ts={ts}")
