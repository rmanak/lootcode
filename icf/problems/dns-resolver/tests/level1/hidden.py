"""Level 1 — address records (hidden cases)."""
from icf_testkit import case, expect


@case("a re-added address goes to the end of the list")
def readd_moves_to_end(Resolver):
    r = Resolver()
    for i, ip in enumerate(["1", "2", "3"], start=1):
        r.add_record(i, "n", ip)
    r.remove_record(4, "n", "1")
    r.add_record(5, "n", "1")
    expect(r.resolve(6, "n"), ["2", "3", "1"])


@case("only one trailing dot is part of the normalization")
def trailing_dot(Resolver):
    r = Resolver()
    r.add_record(1, "a.b.", "9")
    expect(r.resolve(2, "a.b"), ["9"])
    expect(r.resolve(3, "A.B"), ["9"])
    expect(r.resolve(4, "a.b.c"), None)


@case("addresses are compared exactly as given")
def ip_exact(Resolver):
    r = Resolver()
    r.add_record(1, "n", "10.0.0.1")
    expect(r.add_record(2, "n", "10.000.0.1"), True, "different text, different address")
    expect(r.remove_record(3, "n", "10.0.0.01"), False)
    expect(r.resolve(4, "n"), ["10.0.0.1", "10.000.0.1"])


@case("removing from an unknown name returns False")
def remove_unknown(Resolver):
    r = Resolver()
    expect(r.remove_record(1, "x", "1"), False)
    r.add_record(2, "x", "1")
    expect(r.remove_record(3, "x", "2"), False)
    expect(r.resolve(4, "x"), ["1"])


@case("many names stay independent")
def many(Resolver):
    r = Resolver()
    for i in range(100):
        r.add_record(i + 1, f"host{i}.net", f"10.0.0.{i}")
    for i in range(100):
        expect(r.resolve(200 + i, f"HOST{i}.NET."), [f"10.0.0.{i}"])
