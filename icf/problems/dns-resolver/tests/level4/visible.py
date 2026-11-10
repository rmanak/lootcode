"""Level 4 — records that expire (visible cases)."""
from icf_testkit import case, expect


@case("a record with a TTL lives on [timestamp, timestamp + ttl)")
def record_ttl(Resolver):
    r = Resolver()
    r.add_record_with_ttl(10, "a", "1", 5)
    expect(r.resolve(14, "a"), ["1"])
    expect(r.resolve(15, "a"), None)


@case("an alias with a TTL stops being followed when it expires")
def alias_ttl(Resolver):
    r = Resolver()
    r.add_record(1, "b", "2")
    r.add_alias_with_ttl(2, "a", "b", 10)
    expect(r.resolve(11, "a"), ["2"])
    expect(r.resolve(12, "a"), None)
    expect(r.add_record(13, "a", "3"), True, "the name is free again")


@case("the answer TTL is the shortest remaining lifetime it relied on")
def answer_ttl(Resolver):
    r = Resolver()
    r.add_record_with_ttl(1, "b", "1", 100)     # until 101
    r.add_alias_with_ttl(2, "a", "b", 30)       # until 32
    expect(r.get_answer_ttl(12, "a"), 20)
    expect(r.get_answer_ttl(40, "b"), 61)
    expect(r.get_answer_ttl(41, "a"), None)


@case("an answer from permanent records has TTL -1")
def permanent(Resolver):
    r = Resolver()
    r.add_record(1, "a", "1")
    expect(r.get_answer_ttl(2, "a"), -1)
    expect(r.get_answer_ttl(3, "zzz"), None)
