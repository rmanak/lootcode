"""Level 1 — records and fields (hidden cases)."""
import random

from icf_testkit import case, expect


@case("many records and fields round-trip independently")
def many_round_trip(Database):
    db = Database()
    ts = 0
    for r in range(12):
        for f in range(8):
            ts += 1
            db.set(ts, f"rec{r}", f"field{f}", f"{r}-{f}")
    for r in range(12):
        for f in range(8):
            ts += 1
            expect(db.get(ts, f"rec{r}", f"field{f}"), f"{r}-{f}")


@case("a field can be re-created after it is deleted")
def delete_then_set(Database):
    db = Database()
    db.set(1, "k", "f", "first")
    db.delete(2, "k", "f")
    db.set(3, "k", "f", "second")
    expect(db.get(4, "k", "f"), "second")
    expect(db.delete(5, "k", "f"), True)


@case("deleting the last field leaves the record usable")
def empty_record_still_works(Database):
    db = Database()
    db.set(1, "k", "only", "v")
    expect(db.delete(2, "k", "only"), True)
    expect(db.get(3, "k", "only"), None)
    db.set(4, "k", "other", "w")
    expect(db.get(5, "k", "other"), "w")


@case("compare_and_set to the value already stored still reports True")
def compare_and_set_noop(Database):
    db = Database()
    db.set(1, "k", "f", "same")
    expect(db.compare_and_set(2, "k", "f", "same", "same"), True)
    expect(db.get(3, "k", "f"), "same")


@case("values are opaque strings — punctuation and emptiness are preserved")
def values_are_opaque(Database):
    db = Database()
    db.set(1, "k", "a", "x(y), z")
    db.set(2, "k", "b", "")
    db.set(3, "k", "c", "  padded  ")
    expect(db.get(4, "k", "a"), "x(y), z")
    expect(db.get(5, "k", "b"), "", "an empty value is a value, not an absence")
    expect(db.get(6, "k", "c"), "  padded  ")


@case("an empty value still satisfies compare_and_set")
def compare_and_set_empty_value(Database):
    db = Database()
    db.set(1, "k", "f", "")
    expect(db.compare_and_set(2, "k", "f", "", "filled"), True)
    expect(db.get(3, "k", "f"), "filled")


@case("compare_and_set failing leaves the field exactly as it was")
def failed_cas_is_inert(Database):
    db = Database()
    db.set(1, "k", "f", "keep")
    for attempt in ("KEEP", "kee", "keep ", ""):
        expect(db.compare_and_set(2, "k", "f", attempt, "changed"), False,
               f"expected value {attempt!r} does not match 'keep'")
    expect(db.get(3, "k", "f"), "keep")


@case("a long random sequence of operations matches a reference model")
def fuzz_against_model(Database):
    # The model keeps an append-only log per (key, field) and answers by
    # looking at the last write — a different shape from any store you would
    # build, which is the point of comparing against it.
    log = {}

    def model_get(key, field):
        entries = log.get((key, field))
        if not entries:
            return None
        value, deleted = entries[-1]
        return None if deleted else value

    db = Database()
    rng = random.Random(20260912)
    keys = ["k1", "k2", "k3"]
    fields = ["a", "b", "c", "d"]
    for ts in range(1, 600):
        key, field = rng.choice(keys), rng.choice(fields)
        op = rng.random()
        if op < 0.45:
            value = f"v{rng.randrange(5)}"
            db.set(ts, key, field, value)
            log.setdefault((key, field), []).append((value, False))
        elif op < 0.65:
            expected_removed = model_get(key, field) is not None
            expect(db.delete(ts, key, field), expected_removed,
                   f"delete({key!r}, {field!r}) at ts={ts}")
            if expected_removed:
                log[(key, field)].append((None, True))
        elif op < 0.85:
            expected_value = f"v{rng.randrange(5)}"
            new_value = f"n{rng.randrange(5)}"
            current = model_get(key, field)
            should_write = current is not None and current == expected_value
            expect(db.compare_and_set(ts, key, field, expected_value, new_value),
                   should_write, f"compare_and_set at ts={ts}")
            if should_write:
                log[(key, field)].append((new_value, False))
        else:
            expect(db.get(ts, key, field), model_get(key, field),
                   f"get({key!r}, {field!r}) at ts={ts}")
