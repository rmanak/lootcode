"""Level 1 — address records (visible cases)."""
from icf_testkit import case, expect


@case("a name resolves to its addresses in the order they were added")
def resolve_order(Resolver):
    r = Resolver()
    expect(r.add_record(1, "example.com", "10.0.0.2"), True)
    expect(r.add_record(2, "example.com", "10.0.0.1"), True)
    expect(r.resolve(3, "example.com"), ["10.0.0.2", "10.0.0.1"])


@case("an unknown name resolves to None")
def unknown(Resolver):
    r = Resolver()
    r.add_record(1, "a.com", "1.1.1.1")
    expect(r.resolve(2, "b.com"), None)
    expect(r.resolve(3, "a.com"), ["1.1.1.1"])


@case("the same address cannot be added twice to a name")
def duplicate(Resolver):
    r = Resolver()
    r.add_record(1, "a.com", "1.1.1.1")
    expect(r.add_record(2, "a.com", "1.1.1.1"), False)
    expect(r.add_record(3, "b.com", "1.1.1.1"), True, "another name may share it")
    expect(r.resolve(4, "a.com"), ["1.1.1.1"])


@case("names ignore case and one trailing dot")
def normalization(Resolver):
    r = Resolver()
    r.add_record(1, "Example.COM.", "1.2.3.4")
    expect(r.resolve(2, "example.com"), ["1.2.3.4"])
    expect(r.resolve(3, "EXAMPLE.com."), ["1.2.3.4"])
    expect(r.add_record(4, "example.com", "1.2.3.4"), False, "the same name")


@case("removing records")
def remove(Resolver):
    r = Resolver()
    r.add_record(1, "a.com", "1.1.1.1")
    r.add_record(2, "a.com", "2.2.2.2")
    expect(r.remove_record(3, "a.com", "1.1.1.1"), True)
    expect(r.resolve(4, "a.com"), ["2.2.2.2"])
    expect(r.remove_record(5, "a.com", "1.1.1.1"), False)
    expect(r.remove_record(6, "A.COM.", "2.2.2.2"), True)
    expect(r.resolve(7, "a.com"), None, "no addresses left")
