"""Level 1 — items (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a refused copy changes neither item")
def refused_copy_is_inert(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/a", 10)
    inv.add_item("/b", 20)
    expect(inv.copy_item("/a", "/b"), False)
    expect(inv.get_item_quantity("/a"), 10)
    expect(inv.get_item_quantity("/b"), 20)


@case("a copy of a copy is another separate item")
def copy_of_copy(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/a", 7)
    expect(inv.copy_item("/a", "/b"), True)
    expect(inv.copy_item("/b", "/c"), True)
    expect(inv.get_item_quantity("/c"), 7)
    expect(inv.add_item("/c", 1), False, "the copy is a real item")
    expect(inv.copy_item("/a", "/c"), False)


@case("copying an item onto itself is refused")
def copy_onto_itself(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/a", 5)
    expect(inv.copy_item("/a", "/a"), False)
    expect(inv.get_item_quantity("/a"), 5)


@case("names are case-sensitive and compared whole")
def names_exact(InventoryManager):
    inv = InventoryManager()
    expect(inv.add_item("/Bolts", 1), True)
    expect(inv.add_item("/bolts", 2), True, "a different name")
    expect(inv.get_item_quantity("/Bolts"), 1)
    expect(inv.get_item_quantity("/bolt"), None)
    expect(inv.get_item_quantity("/bolts "), None)


@case("slashes and dots have no special meaning in a name")
def plain_string_names(InventoryManager):
    inv = InventoryManager()
    for quantity, name in enumerate(("/a/b", "/a/b/", "a/b", "/a/b.txt", "/a//b"), start=1):
        expect(inv.add_item(name, quantity), True, f"{name!r} is its own name")
    expect(inv.get_item_quantity("/a/b/"), 2)
    expect(inv.get_item_quantity("/a//b"), 5)


@case("large quantities are stored exactly")
def large_quantities(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/x", 10**12 + 7)
    inv.copy_item("/x", "/y")
    expect(inv.get_item_quantity("/y"), 10**12 + 7)


@case("adds, copies and reads match a reference model over a random workload")
def fuzz_against_model(InventoryManager):
    rng = random.Random(1234)
    inv = InventoryManager()
    model = {}
    names = ["/a", "/b", "/c", "/w/a", "/w/b", "/A"]
    for step in range(600):
        roll = rng.random()
        if roll < 0.35:
            name, quantity = rng.choice(names), rng.randrange(1, 100)
            ok = name not in model
            expect(inv.add_item(name, quantity), ok, f"add_item({name}) at step {step}")
            if ok:
                model[name] = quantity
        elif roll < 0.65:
            source, target = rng.choice(names), rng.choice(names)
            ok = source in model and target not in model
            expect(inv.copy_item(source, target), ok,
                   f"copy_item({source}, {target}) at step {step}")
            if ok:
                model[target] = model[source]
        else:
            name = rng.choice(names)
            expect(inv.get_item_quantity(name), model.get(name),
                   f"get_item_quantity({name}) at step {step}")
