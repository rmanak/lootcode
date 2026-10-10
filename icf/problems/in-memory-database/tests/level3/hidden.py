"""Level 3 — fields that expire (hidden cases)."""
import random

from icf_testkit import case, expect


@case("one field's lifetime does not touch its neighbours")
def ttl_is_per_field(Database):
    db = Database()
    db.set_with_ttl(1, "k", "a", "1", 3)
    db.set_with_ttl(1, "k", "b", "2", 30)
    db.set(1, "k", "c", "3")
    expect(db.scan(4, "k"), "b(2), c(3)")
    expect(db.scan(31, "k"), "c(3)")


@case("a ttl of zero means the field is already gone")
def zero_ttl(Database):
    db = Database()
    db.set_with_ttl(5, "k", "f", "v", 0)
    expect(db.get(5, "k", "f"), None, "[5, 5) contains no timestamp")
    expect(db.scan(5, "k"), "")


@case("shortening a lifetime with a second set_with_ttl takes effect")
def ttl_can_shrink(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "v", 100)
    db.set_with_ttl(2, "k", "f", "w", 3)
    expect(db.get(4, "k", "f"), "w")
    expect(db.get(5, "k", "f"), None, "the new, shorter lifetime wins")


@case("a record whose every field expired scans as empty but still accepts writes")
def record_fully_expired(Database):
    db = Database()
    db.set_with_ttl(1, "k", "a", "1", 2)
    db.set_with_ttl(1, "k", "b", "2", 2)
    expect(db.scan(3, "k"), "")
    db.set(4, "k", "c", "3")
    expect(db.scan(5, "k"), "c(3)")


@case("compare_and_set neither extends nor removes a lifetime")
def cas_preserves_expiry(Database):
    db = Database()
    db.set_with_ttl(10, "k", "f", "a", 10)          # [10, 20)
    db.compare_and_set(12, "k", "f", "a", "b")
    db.compare_and_set(14, "k", "f", "b", "c")
    expect(db.get(19, "k", "f"), "c")
    expect(db.get(20, "k", "f"), None, "still expiring at 10 + 10")


@case("a permanent field stays permanent no matter how far the clock runs")
def permanent_is_permanent(Database):
    db = Database()
    db.set(1, "k", "f", "v")
    expect(db.get(10 ** 12, "k", "f"), "v")
    expect(db.scan(10 ** 12, "k"), "f(v)")


@case("expiry is evaluated per call, not at write time")
def expiry_is_lazy(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "v", 10)
    # No call happens between 1 and 11, so an implementation that only sweeps
    # on write has never had the chance to remove this field.
    expect(db.get(11, "k", "f"), None)
    expect(db.delete(12, "k", "f"), False)


@case("a random workload with lifetimes matches a reference model")
def fuzz_with_ttls(Database):
    # The model stores, per field, the write timestamp and the deadline (or
    # None), and re-derives liveness on every question.
    state = {}

    def live(field, ts):
        entry = state.get(field)
        if entry is None:
            return None
        value, deadline = entry
        if deadline is not None and ts >= deadline:
            return None
        return value

    db = Database()
    rng = random.Random(90210)
    fields = ["a", "b", "c"]
    for ts in range(1, 700):
        field = rng.choice(fields)
        roll = rng.random()
        if roll < 0.25:
            value = f"v{rng.randrange(4)}"
            db.set(ts, "k", field, value)
            state[field] = (value, None)
        elif roll < 0.55:
            value = f"t{rng.randrange(4)}"
            ttl = rng.choice([1, 2, 5, 12, 40])
            db.set_with_ttl(ts, "k", field, value, ttl)
            state[field] = (value, ts + ttl)
        elif roll < 0.65:
            present = live(field, ts) is not None
            expect(db.delete(ts, "k", field), present, f"delete at ts={ts}")
            if present:
                state.pop(field, None)
        elif roll < 0.75:
            expected = f"v{rng.randrange(4)}"
            current = live(field, ts)
            should = current is not None and current == expected
            expect(db.compare_and_set(ts, "k", field, expected, "cas"), should,
                   f"compare_and_set at ts={ts}")
            if should:
                state[field] = ("cas", state[field][1])
        elif roll < 0.9:
            expect(db.get(ts, "k", field), live(field, ts), f"get at ts={ts}")
        else:
            alive = {f: live(f, ts) for f in fields}
            wanted = ", ".join(f"{f}({v})" for f, v in sorted(alive.items())
                               if v is not None)
            expect(db.scan(ts, "k"), wanted, f"scan at ts={ts}")
