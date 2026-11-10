"""Level 4 — records that expire (hidden cases)."""
from icf_testkit import case, expect


@case("an expired address can be added again, at the end of the list")
def readd_expired(Resolver):
    r = Resolver()
    r.add_record_with_ttl(1, "n", "1", 5)
    r.add_record(2, "n", "2")
    expect(r.add_record(3, "n", "1"), False, "still alive")
    expect(r.add_record(6, "n", "1"), True)
    expect(r.resolve(7, "n"), ["2", "1"])


@case("expired records cannot be removed")
def remove_expired(Resolver):
    r = Resolver()
    r.add_record_with_ttl(1, "n", "1", 2)
    r.add_alias_with_ttl(1 + 1, "m", "n", 2)
    expect(r.remove_record(10, "n", "1"), False)
    expect(r.remove_alias(11, "m"), False)


@case("a ttl of 0 is already expired")
def ttl_zero(Resolver):
    r = Resolver()
    expect(r.add_record_with_ttl(1, "n", "1", 0), True)
    expect(r.resolve(2, "n"), None)
    expect(r.add_alias(3, "n", "m"), True, "nothing alive is in the way")


@case("the answer TTL counts every alias on the path and every address returned")
def ttl_path(Resolver):
    r = Resolver()
    r.add_alias_with_ttl(1, "a", "b", 50)       # 51
    r.add_alias_with_ttl(2, "b", "c", 40)       # 42
    r.add_record_with_ttl(3, "c", "1", 90)      # 93
    r.add_record_with_ttl(4, "c", "2", 30)      # 34
    r.add_record(5, "c", "3")
    expect(r.get_answer_ttl(10, "a"), 24)
    expect(r.resolve(34, "a"), ["1", "3"])
    expect(r.get_answer_ttl(35, "a"), 7)
    expect(r.get_answer_ttl(42, "a"), None, "b's alias is gone, so a ends at b")
    expect(r.get_answer_ttl(43, "c"), 50)


@case("through a fallback, only the path that answered counts")
def ttl_fallback(Resolver):
    r = Resolver()
    r.add_alias_with_ttl(1, "main", "gone", 5)  # until 6, dead end
    r.add_record_with_ttl(2, "backup", "9", 100)
    r.add_fallback(3, "main", "backup")
    expect(r.get_answer_ttl(4, "main"), 98)
    expect(r.get_status(7, "main"), "RESOLVED")


@case("a loop formed by an alias that expires is a loop only while it lives")
def loop_expires(Resolver):
    r = Resolver()
    r.add_record(1, "safe", "1")
    r.add_alias(2, "a", "b")
    r.add_alias_with_ttl(3, "b", "a", 10)       # until 13
    r.add_fallback(4, "a", "safe")
    expect(r.get_status(5, "a"), "LOOP")
    expect(r.get_status(13, "a"), "RESOLVED")
    expect(r.resolve(14, "a"), ["1"], "b has no alias now, so a falls back")


@case("an alias and an address can't overlap, but can follow each other")
def exclusive_over_time(Resolver):
    r = Resolver()
    r.add_record_with_ttl(1, "x", "1", 10)
    expect(r.add_alias(2, "x", "y"), False)
    expect(r.add_alias(11, "x", "y"), True)
    expect(r.add_record(12, "x", "2"), False)
    expect(r.get_chain(13, "x"), ["x", "y"])
