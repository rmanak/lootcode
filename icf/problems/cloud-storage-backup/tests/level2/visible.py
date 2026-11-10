"""Level 2 — the largest files (visible cases)."""
from icf_testkit import case, expect


@case("the largest files with a prefix, largest first")
def largest(CloudStorage):
    s = CloudStorage()
    s.add_file("img/a.png", 300)
    s.add_file("img/b.png", 900)
    s.add_file("doc/c.txt", 1000)
    s.add_file("img/c.png", 500)
    expect(s.get_n_largest("img/", 2), ["img/b.png(900)", "img/c.png(500)"])


@case("ties are broken by name, and n may exceed the matches")
def ties(CloudStorage):
    s = CloudStorage()
    s.add_file("b", 5)
    s.add_file("a", 5)
    s.add_file("c", 9)
    expect(s.get_n_largest("", 10), ["c(9)", "a(5)", "b(5)"])


@case("no match gives an empty list")
def no_match(CloudStorage):
    s = CloudStorage()
    s.add_file("a", 1)
    expect(s.get_n_largest("z", 3), [])
    expect(s.get_n_largest("a", 3), ["a(1)"])
