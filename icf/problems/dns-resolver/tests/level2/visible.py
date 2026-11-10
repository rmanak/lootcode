"""Level 2 — aliases (visible cases)."""
from icf_testkit import case, expect


@case("an alias resolves to its target's addresses")
def alias(Resolver):
    r = Resolver()
    r.add_record(1, "real.com", "1.1.1.1")
    expect(r.add_alias(2, "www.com", "real.com"), True)
    expect(r.resolve(3, "www.com"), ["1.1.1.1"])


@case("aliases chain")
def chain(Resolver):
    r = Resolver()
    r.add_record(1, "c", "3.3.3.3")
    r.add_alias(2, "a", "b")
    r.add_alias(3, "b", "c")
    expect(r.resolve(4, "a"), ["3.3.3.3"])
    expect(r.get_chain(5, "A."), ["a", "b", "c"])


@case("a chain that ends nowhere resolves to None")
def dead_end(Resolver):
    r = Resolver()
    r.add_alias(1, "a", "b")
    expect(r.resolve(2, "a"), None)
    expect(r.get_chain(3, "a"), ["a", "b"])


@case("a loop resolves to None, and the chain shows the repeat")
def loop(Resolver):
    r = Resolver()
    r.add_alias(1, "a", "b")
    r.add_alias(2, "b", "a")
    expect(r.resolve(3, "a"), None)
    expect(r.get_chain(4, "a"), ["a", "b", "a"])


@case("a name is either an alias or has addresses, never both")
def exclusive(Resolver):
    r = Resolver()
    r.add_record(1, "x", "1")
    expect(r.add_alias(2, "x", "y"), False)
    r.add_alias(3, "y", "x")
    expect(r.add_record(4, "y", "2"), False)
    expect(r.resolve(5, "y"), ["1"])
