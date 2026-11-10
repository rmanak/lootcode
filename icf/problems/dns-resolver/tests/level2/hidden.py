"""Level 2 — aliases (hidden cases)."""
from icf_testkit import case, expect


@case("one alias per name, and never to itself")
def alias_rules(Resolver):
    r = Resolver()
    expect(r.add_alias(1, "a", "A."), False, "the same name after normalization")
    expect(r.add_alias(2, "a", "b"), True)
    expect(r.add_alias(3, "a", "c"), False)
    expect(r.get_chain(4, "a"), ["a", "b"])


@case("removing an alias makes the name free again")
def remove_alias(Resolver):
    r = Resolver()
    r.add_alias(1, "a", "b")
    expect(r.remove_alias(2, "A"), True)
    expect(r.remove_alias(3, "a"), False)
    expect(r.add_record(4, "a", "1"), True)
    expect(r.resolve(5, "a"), ["1"])


@case("a chain without aliases is the name alone, normalized")
def chain_of_one(Resolver):
    r = Resolver()
    expect(r.get_chain(1, "Nothing.Here."), ["nothing.here"])
    r.add_record(2, "x", "1")
    expect(r.get_chain(3, "X"), ["x"])


@case("a loop that does not return to the start is still a loop")
def tail_loop(Resolver):
    r = Resolver()
    r.add_alias(1, "a", "b")
    r.add_alias(2, "b", "c")
    r.add_alias(3, "c", "b")
    expect(r.get_chain(4, "a"), ["a", "b", "c", "b"])
    expect(r.resolve(5, "a"), None)


@case("aliases to normalized targets")
def normalized_targets(Resolver):
    r = Resolver()
    r.add_record(1, "target.org", "5")
    r.add_alias(2, "src", "TARGET.ORG.")
    expect(r.get_chain(3, "src"), ["src", "target.org"])
    expect(r.resolve(4, "src"), ["5"])


@case("an alias can be created before its target exists")
def forward_reference(Resolver):
    r = Resolver()
    r.add_alias(1, "a", "b")
    expect(r.resolve(2, "a"), None)
    r.add_record(3, "b", "7")
    expect(r.resolve(4, "a"), ["7"])
    r.remove_record(5, "b", "7")
    expect(r.resolve(6, "a"), None)


@case("a long chain resolves")
def long_chain(Resolver):
    r = Resolver()
    for i in range(300):
        r.add_alias(i + 1, f"n{i}", f"n{i + 1}")
    r.add_record(400, "n300", "9")
    expect(r.resolve(401, "n0"), ["9"])
    expect(len(r.get_chain(402, "n0")), 301)
