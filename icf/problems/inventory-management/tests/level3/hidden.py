"""Level 3 — users and capacity (hidden cases)."""
import random

from icf_testkit import case, expect


@case("raising the capacity removes nothing and makes room for more")
def raise_capacity(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 100)
    expect(inv.add_item_by("u", "/a", 100), 0)
    expect(inv.update_capacity("u", 300), 0)
    expect(inv.add_item_by("u", "/b", 150), 50)


@case("items added with add_item count against no user's capacity")
def admin_items_unlimited(InventoryManager):
    inv = InventoryManager()
    expect(inv.add_item("/big", 10**6), True)
    inv.add_user("u", 10)
    expect(inv.add_item_by("u", "/small", 10), 0)
    expect(inv.update_capacity("u", 0), 1, "only the user's own item is removed")
    expect(inv.get_item_quantity("/big"), 10**6)
    expect(inv.get_item_quantity("/small"), None)


@case("a copy that would not fit is refused")
def copy_does_not_fit(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 100)
    expect(inv.add_item_by("u", "/a", 60), 40)
    expect(inv.copy_item("/a", "/b"), False)
    expect(inv.get_item_quantity("/b"), None)
    expect(inv.add_item_by("u", "/c", 40), 0, "the refused copy used nothing")


@case("items removed by update_capacity free their names")
def removal_frees_names(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 100)
    inv.add_item_by("u", "/a", 80)
    expect(inv.update_capacity("u", 50), 1)
    expect(inv.get_item_quantity("/a"), None)
    expect(inv.add_item_by("u", "/a", 50), 0)


@case("update_capacity returns None for an unknown user")
def update_unknown(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 10)
    expect(inv.update_capacity("u", 20), 0)
    expect(inv.update_capacity("ghost", 5), None)


@case("each user's capacity is separate")
def separate_capacities(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u1", 100)
    inv.add_user("u2", 100)
    expect(inv.add_item_by("u1", "/a", 100), 0)
    expect(inv.add_item_by("u2", "/b", 60), 40)
    expect(inv.update_capacity("u1", 50), 1)
    expect(inv.get_item_quantity("/b"), 60, "u2's item is untouched")


@case("a refused add_user keeps the original capacity")
def refused_add_user(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 10)
    expect(inv.add_user("u", 1000), False)
    expect(inv.add_item_by("u", "/a", 11), None)
    expect(inv.add_item_by("u", "/a", 10), 0)


@case("shrinking the capacity to 0 removes every item the user owns")
def shrink_to_zero(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 100)
    for name, quantity in (("/a", 30), ("/b", 30), ("/c", 40)):
        inv.add_item_by("u", name, quantity)
    expect(inv.update_capacity("u", 0), 3)
    expect(inv.find_items("", ""), [])
    expect(inv.add_item_by("u", "/d", 1), None)


@case("update_capacity stops as soon as the remaining items fit")
def stops_early(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 1000)
    inv.add_item_by("u", "/big", 500)
    inv.add_item_by("u", "/s1", 10)
    inv.add_item_by("u", "/s2", 10)
    expect(inv.update_capacity("u", 20), 1)
    expect(inv.get_item_quantity("/s1"), 10)
    expect(inv.get_item_quantity("/s2"), 10)


@case("copying an item added with add_item makes another unlimited item")
def copy_admin_item(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 0)
    inv.add_item("/x", 50)
    expect(inv.copy_item("/x", "/y"), True)
    expect(inv.update_capacity("u", 0), 0)
    expect(inv.get_item_quantity("/y"), 50)


@case("capacity rules match a reference model over a random workload")
def fuzz_against_model(InventoryManager):
    rng = random.Random(8642)
    inv = InventoryManager()
    items = {}   # name -> [quantity, owner]
    caps = {}
    names = ["/a", "/b", "/c", "/d", "/e", "/f", "/g"]

    def used(user):
        return sum(q for q, owner in items.values() if owner == user)

    for step in range(900):
        roll = rng.random()
        user = rng.choice(["u1", "u2", "u3"])
        name = rng.choice(names)
        if roll < 0.08:
            capacity = rng.randrange(0, 300)
            ok = user not in caps
            expect(inv.add_user(user, capacity), ok, f"add_user({user}) at step {step}")
            if ok:
                caps[user] = capacity
        elif roll < 0.15:
            quantity = rng.randrange(1, 80)
            ok = name not in items
            expect(inv.add_item(name, quantity), ok, f"add_item({name}) at step {step}")
            if ok:
                items[name] = [quantity, "admin"]
        elif roll < 0.4:
            quantity = rng.randrange(1, 120)
            ok = user in caps and name not in items and used(user) + quantity <= caps[user]
            want = caps[user] - used(user) - quantity if ok else None
            expect(inv.add_item_by(user, name, quantity), want,
                   f"add_item_by({user}, {name}, {quantity}) at step {step}")
            if ok:
                items[name] = [quantity, user]
        elif roll < 0.55:
            source, target = rng.choice(names), rng.choice(names)
            ok = source in items and target not in items
            if ok:
                quantity, owner = items[source]
                ok = owner == "admin" or used(owner) + quantity <= caps[owner]
            expect(inv.copy_item(source, target), ok,
                   f"copy_item({source}, {target}) at step {step}")
            if ok:
                items[target] = list(items[source])
        elif roll < 0.65:
            capacity = rng.randrange(0, 300)
            want = None
            if user in caps:
                caps[user] = capacity
                want = 0
                for owned in sorted((n for n in items if items[n][1] == user),
                                    key=lambda n: (-items[n][0], n)):
                    if used(user) <= capacity:
                        break
                    del items[owned]
                    want += 1
            expect(inv.update_capacity(user, capacity), want,
                   f"update_capacity({user}, {capacity}) at step {step}")
        elif roll < 0.85:
            expect(inv.get_item_quantity(name), items[name][0] if name in items else None,
                   f"get_item_quantity({name}) at step {step}")
        else:
            ranked = sorted(items, key=lambda n: (-items[n][0], n))
            expect(inv.find_items("", ""), [f"{n}({items[n][0]})" for n in ranked],
                   f"find_items at step {step}")
