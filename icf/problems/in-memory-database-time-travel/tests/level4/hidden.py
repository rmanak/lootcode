"""Level 4 — reading the past (hidden cases)."""
import random

from icf_testkit import case, expect


@case("an expired version does not fall back to an older permanent value")
def expired_no_fallback(Database):
    db = Database()
    db.set(1, "k", "f", "perm")
    db.set_with_ttl(2, "k", "f", "temp", 3)   # alive on [2, 5)
    expect(db.get_when(10, "k", "f", 1), "perm")
    expect(db.get_when(11, "k", "f", 4), "temp")
    expect(db.get_when(12, "k", "f", 5), None)
    expect(db.get_when(13, "k", "f", 9), None)


@case("compare_and_set history keeps the lifetime it inherited")
def cas_history(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "a", 10)     # until 11
    db.compare_and_set(4, "k", "f", "a", "b")
    expect(db.get_when(20, "k", "f", 3), "a")
    expect(db.get_when(21, "k", "f", 10), "b")
    expect(db.get_when(22, "k", "f", 11), None)


@case("failed conditional writes leave no trace in history")
def failed_writes(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    db.compare_and_set(2, "k", "f", "zzz", "b")
    db.compare_and_delete(3, "k", "f", "zzz")
    expect(db.get_when(10, "k", "f", 3), "a")


@case("a field re-created after a delete has a gap in its history")
def gap(Database):
    db = Database()
    db.set(1, "k", "f", "a")
    db.compare_and_delete(2, "k", "f", "a")
    db.set(5, "k", "f", "b")
    expect(db.get_when(10, "k", "f", 1), "a")
    expect(db.get_when(11, "k", "f", 3), None)
    expect(db.get_when(12, "k", "f", 5), "b")


@case("get_when at the present moment agrees with get")
def present(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "a", 100)
    expect(db.get_when(50, "k", "f", 50), db.get(51, "k", "f"))
    expect(db.get_when(52, "k", "f", 52), "a")


def build(seed):
    rng = random.Random(seed)
    writes = []          # (ts, field, value or None, expires or None)
    calls = []
    current = {}         # field -> (value, expires)

    def alive(entry, t):
        return entry is not None and entry[0] is not None and (entry[1] is None or t < entry[1])

    ts = 0
    for _ in range(250):
        ts += rng.randint(1, 3)
        field = rng.choice("abc")
        entry = current.get(field)
        op = rng.random()
        if op < 0.3:
            value = rng.choice("xyz")
            current[field] = (value, None)
            calls.append(("set", ts, field, value))
        elif op < 0.55:
            value, ttl = rng.choice("xyz"), rng.randint(0, 8)
            current[field] = (value, ts + ttl)
            calls.append(("ttl", ts, field, value, ttl))
        elif op < 0.7:
            value = rng.choice("xyz")
            if alive(entry, ts) and entry[0] == value:
                current[field] = (rng.choice("pq"), entry[1])
                calls.append(("cas", ts, field, value, current[field][0], True))
            else:
                calls.append(("cas", ts, field, value, "pq"[0], False))
        elif op < 0.8:
            value = rng.choice("xyzpq")
            if alive(entry, ts) and entry[0] == value:
                current[field] = (None, None)
                calls.append(("cad", ts, field, value, True))
            else:
                calls.append(("cad", ts, field, value, False))
        else:
            continue
        writes.append((ts, field, current.get(field)))
    return calls, writes, ts


def expected_at(writes, field, t):
    last = None
    for wts, f, entry in writes:
        if f == field and wts <= t:
            last = entry
    if last is None or last[0] is None or (last[1] is not None and t >= last[1]):
        return None
    return last[0]


@case("random histories match a reference model at every moment")
def random_model(Database):
    for seed in (11, 12):
        calls, writes, end = build(seed)
        db = Database()
        for call in calls:
            if call[0] == "set":
                db.set(call[1], "k", call[2], call[3])
            elif call[0] == "ttl":
                db.set_with_ttl(call[1], "k", call[2], call[3], call[4])
            elif call[0] == "cas":
                expect(db.compare_and_set(call[1], "k", call[2], call[3], call[4]), call[5])
            else:
                expect(db.compare_and_delete(call[1], "k", call[2], call[3]), call[4])
        now = end + 1
        for t in range(0, end + 1):
            for field in "abc":
                now += 1
                expect(db.get_when(now, "k", field, t), expected_at(writes, field, t),
                       f"field {field} at {t}")
