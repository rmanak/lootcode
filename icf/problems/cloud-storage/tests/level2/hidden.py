"""Level 2 — finding files (hidden cases)."""
import random

from icf_testkit import case, expect


@case("an empty prefix or suffix matches every name on that side")
def empty_sides(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a/x", 1)
    storage.add_file("/b/x", 2)
    storage.add_file("/a/y", 3)
    expect(storage.find_file("", ""), ["/a/y(3)", "/b/x(2)", "/a/x(1)"])
    expect(storage.find_file("/a", ""), ["/a/y(3)", "/a/x(1)"])
    expect(storage.find_file("", "x"), ["/b/x(2)", "/a/x(1)"])


@case("the prefix and suffix may overlap within one name")
def overlapping_prefix_suffix(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/ab", 1)
    storage.add_file("/a", 2)
    storage.add_file("/b", 3)
    expect(storage.find_file("/a", "b"), ["/ab(1)"])
    expect(storage.find_file("/ab", "/ab"), ["/ab(1)"])
    expect(storage.find_file("/a", "/a"), ["/a(2)"])


@case("copies appear in the results")
def copies_found(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/music/one.mp3", 4)
    storage.copy_file("/music/one.mp3", "/music/two.mp3")
    expect(storage.find_file("/music/", ".mp3"), ["/music/one.mp3(4)", "/music/two.mp3(4)"])


@case("matching is case-sensitive")
def case_sensitive(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/Docs/Notes.TXT", 5)
    storage.add_file("/docs/notes.txt", 6)
    expect(storage.find_file("/docs", ""), ["/docs/notes.txt(6)"])
    expect(storage.find_file("", ".TXT"), ["/Docs/Notes.TXT(5)"])


@case("a prefix matches any name that starts with it, not only whole directories")
def prefix_is_plain(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/dir/x.txt", 1)
    storage.add_file("/dir2/y.txt", 2)
    storage.add_file("/directory/z.txt", 3)
    expect(storage.find_file("/dir", ".txt"),
           ["/directory/z.txt(3)", "/dir2/y.txt(2)", "/dir/x.txt(1)"])
    expect(storage.find_file("/dir/", ".txt"), ["/dir/x.txt(1)"])


@case("names with equal sizes compare as plain strings")
def plain_string_order(CloudStorage):
    storage = CloudStorage()
    for name in ("/f9", "/f10", "/F", "/f.txt", "/f/a"):
        storage.add_file(name, 1)
    expect(storage.find_file("", ""), ["/F(1)", "/f.txt(1)", "/f/a(1)", "/f10(1)", "/f9(1)"])


@case("find_file on an empty storage returns an empty list")
def empty_storage(CloudStorage):
    storage = CloudStorage()
    expect(storage.find_file("", ""), [])
    storage.add_file("/x", 3)
    expect(storage.find_file("", ""), ["/x(3)"])


@case("a refused add or copy does not show up in the results")
def refused_writes_invisible(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a.txt", 10)
    storage.add_file("/b.txt", 20)
    storage.add_file("/a.txt", 99)
    storage.copy_file("/a.txt", "/b.txt")
    storage.copy_file("/missing.txt", "/c.txt")
    expect(storage.find_file("", ".txt"), ["/b.txt(20)", "/a.txt(10)"])


@case("searches match a reference model over a random workload")
def fuzz_against_model(CloudStorage):
    rng = random.Random(97531)
    storage = CloudStorage()
    model = {}
    names = ["/w/a", "/w/ab", "/w/b", "/s/a", "/s/b", "/W/a", "/wa", "/a"]
    for step in range(500):
        roll = rng.random()
        if roll < 0.35:
            name, size = rng.choice(names), rng.randrange(1, 6)
            storage.add_file(name, size)
            model.setdefault(name, size)
        elif roll < 0.55:
            source, target = rng.choice(names), rng.choice(names)
            storage.copy_file(source, target)
            if source in model and target not in model:
                model[target] = model[source]
        else:
            prefix = rng.choice(["", "/", "/w", "/w/", "/s", "/W", "/a"])
            suffix = rng.choice(["", "a", "b", "ab", "/a"])
            matches = sorted((n for n in model if n.startswith(prefix) and n.endswith(suffix)),
                             key=lambda n: (-model[n], n))
            expect(storage.find_file(prefix, suffix), [f"{n}({model[n]})" for n in matches],
                   f"find_file({prefix!r}, {suffix!r}) at step {step}")
