"""Level 3 — fallbacks and errors (hidden cases)."""
from icf_testkit import case, expect


@case("a loop inside a fallback stops the whole resolution")
def loop_in_fallback(Resolver):
    r = Resolver()
    r.add_alias(1, "bad", "bad2")
    r.add_alias(2, "bad2", "bad")
    r.add_record(3, "good", "7")
    r.add_fallback(4, "main", "bad")
    r.add_fallback(5, "main", "good")
    expect(r.get_status(6, "main"), "LOOP")
    expect(r.resolve(7, "main"), None, "good is never reached")


@case("a fallback is resolved fully: aliases and its own fallbacks")
def fallback_recursion(Resolver):
    r = Resolver()
    r.add_record(1, "deep", "4")
    r.add_alias(2, "mid", "nowhere")
    r.add_fallback(3, "mid", "deep")
    r.add_fallback(4, "top", "mid")
    expect(r.resolve(5, "top"), ["4"])


@case("only the queried name's fallbacks are used, not those along its chain")
def chain_fallbacks_ignored(Resolver):
    r = Resolver()
    r.add_alias(1, "a", "b")
    r.add_record(2, "c", "3")
    r.add_fallback(3, "b", "c")
    expect(r.resolve(4, "b"), ["3"], "b's own fallback")
    expect(r.resolve(5, "a"), None, "a has no fallbacks of its own")
    expect(r.get_status(6, "a"), "NOT_FOUND")


@case("fallback cycles end in NOT_FOUND, never forever")
def fallback_cycle(Resolver):
    r = Resolver()
    r.add_fallback(1, "a", "b")
    r.add_fallback(2, "b", "a")
    expect(r.get_status(3, "a"), "NOT_FOUND")
    r.add_fallback(4, "b", "c")
    r.add_record(5, "c", "1")
    expect(r.resolve(6, "a"), ["1"])


@case("a name already attempted is skipped")
def attempted_skipped(Resolver):
    r = Resolver()
    r.add_alias(1, "x", "x2")
    r.add_alias(2, "x2", "x")
    r.add_fallback(3, "a", "b")
    r.add_fallback(4, "b", "a")     # a was attempted already, so it is skipped
    r.add_fallback(5, "a", "c")
    r.add_record(6, "c", "5")
    expect(r.resolve(7, "a"), ["5"])


@case("add_fallback refuses duplicates and the name itself")
def add_fallback_rules(Resolver):
    r = Resolver()
    expect(r.add_fallback(1, "a", "A."), False)
    expect(r.add_fallback(2, "a", "b"), True)
    expect(r.add_fallback(3, "A", "B."), False, "already there after normalization")
    r.add_record(4, "b", "1")
    expect(r.resolve(5, "a."), ["1"])


@case("get_chain ignores fallbacks")
def chain_no_fallback(Resolver):
    r = Resolver()
    r.add_record(1, "b", "1")
    r.add_fallback(2, "a", "b")
    expect(r.get_chain(3, "a"), ["a"])
