"""Level 2 — finding items (hidden cases)."""
import random

from icf_testkit import case, expect


@case("an empty prefix or suffix matches every name on that side")
def empty_sides(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/a/x", 1)
    inv.add_item("/b/x", 2)
    inv.add_item("/a/y", 3)
    expect(inv.find_items("", ""), ["/a/y(3)", "/b/x(2)", "/a/x(1)"])
    expect(inv.find_items("/a", ""), ["/a/y(3)", "/a/x(1)"])
    expect(inv.find_items("", "x"), ["/b/x(2)", "/a/x(1)"])


@case("the prefix and suffix may overlap within a short name")
def overlapping_prefix_suffix(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/ab", 1)
    inv.add_item("/a", 2)
    inv.add_item("/b", 3)
    expect(inv.find_items("/a", "b"), ["/ab(1)"])
    expect(inv.find_items("/ab", "/ab"), ["/ab(1)"])
    expect(inv.find_items("/a", "/a"), ["/a(2)"])


@case("copies appear in the results")
def copies_found(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/w/one", 4)
    inv.copy_item("/w/one", "/w/two")
    expect(inv.find_items("/w/", ""), ["/w/one(4)", "/w/two(4)"])


@case("matching is case-sensitive")
def case_sensitive(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/Tools/Hammer", 5)
    inv.add_item("/tools/hammer", 6)
    expect(inv.find_items("/tools", ""), ["/tools/hammer(6)"])
    expect(inv.find_items("", "Hammer"), ["/Tools/Hammer(5)"])


@case("a prefix matches any name that starts with it, not only whole sections")
def prefix_is_plain(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/warehouse/x", 1)
    inv.add_item("/warehouse2/y", 2)
    expect(inv.find_items("/warehouse", ""), ["/warehouse2/y(2)", "/warehouse/x(1)"])


@case("names with equal quantities compare as plain strings")
def plain_string_order(InventoryManager):
    inv = InventoryManager()
    for name in ("/a9", "/a10", "/B", "/a"):
        inv.add_item(name, 1)
    expect(inv.find_items("", ""), ["/B(1)", "/a(1)", "/a10(1)", "/a9(1)"])


@case("find_items on an empty warehouse returns an empty list")
def empty_warehouse(InventoryManager):
    inv = InventoryManager()
    expect(inv.find_items("", ""), [])
    inv.add_item("/x", 3)
    expect(inv.find_items("", ""), ["/x(3)"])


@case("searches match a reference model over a random workload")
def fuzz_against_model(InventoryManager):
    rng = random.Random(4321)
    inv = InventoryManager()
    model = {}
    names = ["/w/a", "/w/ab", "/w/b", "/s/a", "/s/b", "/W/a", "/wa", "/a"]
    for step in range(500):
        roll = rng.random()
        if roll < 0.35:
            name, quantity = rng.choice(names), rng.randrange(1, 6)
            inv.add_item(name, quantity)
            model.setdefault(name, quantity)
        elif roll < 0.55:
            source, target = rng.choice(names), rng.choice(names)
            inv.copy_item(source, target)
            if source in model and target not in model:
                model[target] = model[source]
        else:
            prefix = rng.choice(["", "/", "/w", "/w/", "/s", "/W", "/a"])
            suffix = rng.choice(["", "a", "b", "ab", "/a"])
            matches = sorted((n for n in model if n.startswith(prefix) and n.endswith(suffix)),
                             key=lambda n: (-model[n], n))
            expect(inv.find_items(prefix, suffix), [f"{n}({model[n]})" for n in matches],
                   f"find_items({prefix!r}, {suffix!r}) at step {step}")
