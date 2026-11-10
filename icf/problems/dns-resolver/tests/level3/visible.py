"""Level 3 — fallbacks and errors (visible cases)."""
from icf_testkit import case, expect


@case("a fallback answers when the name has no addresses")
def fallback(Resolver):
    r = Resolver()
    r.add_record(1, "backup.com", "9.9.9.9")
    expect(r.add_fallback(2, "main.com", "backup.com"), True)
    expect(r.resolve(3, "main.com"), ["9.9.9.9"])
    expect(r.get_status(4, "main.com"), "RESOLVED")


@case("fallbacks are not used when the name resolves on its own")
def primary_wins(Resolver):
    r = Resolver()
    r.add_record(1, "main", "1")
    r.add_record(2, "backup", "2")
    r.add_fallback(3, "main", "backup")
    expect(r.resolve(4, "main"), ["1"])


@case("fallbacks are tried in the order they were added")
def order(Resolver):
    r = Resolver()
    r.add_record(1, "third", "3")
    r.add_record(2, "second", "2")
    r.add_fallback(3, "main", "first")
    r.add_fallback(4, "main", "second")
    r.add_fallback(5, "main", "third")
    expect(r.resolve(6, "main"), ["2"], "first has nothing, second answers")


@case("statuses: RESOLVED, NOT_FOUND and LOOP")
def statuses(Resolver):
    r = Resolver()
    r.add_record(1, "ok", "1")
    r.add_alias(2, "x", "y")
    r.add_alias(3, "y", "x")
    expect(r.get_status(4, "ok"), "RESOLVED")
    expect(r.get_status(5, "nothing"), "NOT_FOUND")
    expect(r.get_status(6, "x"), "LOOP")


@case("a loop is an error: fallbacks are not tried")
def loop_propagates(Resolver):
    r = Resolver()
    r.add_alias(1, "a", "b")
    r.add_alias(2, "b", "a")
    r.add_record(3, "safe", "1")
    r.add_fallback(4, "a", "safe")
    expect(r.resolve(5, "a"), None)
    expect(r.get_status(6, "a"), "LOOP")
