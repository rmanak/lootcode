"""Level 4 — packing items (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a packed item can be copied, and the copy unpacked under its own name")
def copy_packed(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    inv.add_item_by("ana", "/a", 400)
    expect(inv.pack_item("ana", "/a"), 800)
    expect(inv.copy_item("/a.packed", "/b.packed"), True)
    expect(inv.unpack_item("ana", "/b"), 400)
    expect(inv.get_item_quantity("/b"), 400)
    expect(inv.get_item_quantity("/a.packed"), 200)


@case("packing is refused when the packed name is already taken")
def packed_name_taken(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    inv.add_item_by("ana", "/a", 100)
    expect(inv.pack_item("ana", "/a"), 950)
    expect(inv.add_item_by("ana", "/a", 200), 750)
    expect(inv.pack_item("ana", "/a"), None)
    expect(inv.get_item_quantity("/a"), 200)


@case("an already packed item cannot be packed again")
def no_double_packing(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    inv.add_item_by("ana", "/a", 100)
    inv.pack_item("ana", "/a")
    expect(inv.pack_item("ana", "/a.packed"), None)
    expect(inv.get_item_quantity("/a.packed.packed"), None)
    expect(inv.get_item_quantity("/a.packed"), 50)


@case("packed items appear in find_items and are removed by update_capacity like any other")
def packed_items_are_items(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    inv.add_item_by("ana", "/big", 600)
    inv.add_item_by("ana", "/small", 100)
    expect(inv.pack_item("ana", "/big"), 600)
    expect(inv.find_items("/", ""), ["/big.packed(300)", "/small(100)"])
    expect(inv.update_capacity("ana", 150), 1)
    expect(inv.get_item_quantity("/big.packed"), None)
    expect(inv.get_item_quantity("/small"), 100)


@case("unpack_item is refused for an unknown user, a missing packed item, or someone else's")
def unpack_refused(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 100)
    inv.add_user("ben", 100)
    inv.add_item_by("ana", "/a", 40)
    expect(inv.pack_item("ana", "/a"), 80)
    expect(inv.unpack_item("ghost", "/a"), None)
    expect(inv.unpack_item("ben", "/a"), None)
    expect(inv.unpack_item("ana", "/zzz"), None)
    expect(inv.unpack_item("ana", "/a.packed"), None, "the name is given without the suffix")
    expect(inv.unpack_item("ana", "/a"), 60)


@case("an item can be packed and unpacked again and again")
def repeated_round_trips(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 100)
    inv.add_item_by("ana", "/a", 40)
    for _ in range(3):
        expect(inv.pack_item("ana", "/a"), 80)
        expect(inv.unpack_item("ana", "/a"), 60)
    expect(inv.get_item_quantity("/a"), 40)


@case("items added with add_item cannot be packed by a user")
def admin_items_not_packable(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 100)
    inv.add_item("/x", 10)
    expect(inv.pack_item("u", "/x"), None)
    expect(inv.get_item_quantity("/x"), 10)
    expect(inv.add_item_by("u", "/y", 10), 90)
    expect(inv.pack_item("u", "/y"), 95)


@case("unpacking that exactly fills the capacity is allowed")
def unpack_exact_fit(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 100)
    expect(inv.add_item_by("u", "/a", 100), 0)
    expect(inv.pack_item("u", "/a"), 50)
    expect(inv.unpack_item("u", "/a"), 0)


@case("packing, unpacking and capacity match a reference model over a random workload")
def fuzz_against_model(InventoryManager):
    rng = random.Random(3131)
    inv = InventoryManager()
    items = {}   # name -> [quantity, owner]
    caps = {}
    bases = ["/a", "/b", "/c", "/d", "/e"]

    def used(user):
        return sum(q for q, owner in items.values() if owner == user)

    for step in range(1000):
        roll = rng.random()
        user = rng.choice(["u1", "u2", "ghost"])
        base = rng.choice(bases)
        if roll < 0.08:
            capacity = rng.randrange(0, 400)
            ok = user not in caps
            expect(inv.add_user(user, capacity), ok, f"add_user({user}) at step {step}")
            if ok:
                caps[user] = capacity
        elif roll < 0.14:
            quantity = rng.randrange(1, 40) * 2
            ok = base not in items
            expect(inv.add_item(base, quantity), ok, f"add_item({base}) at step {step}")
            if ok:
                items[base] = [quantity, "admin"]
        elif roll < 0.34:
            quantity = rng.randrange(1, 60) * 2
            ok = user in caps and base not in items and used(user) + quantity <= caps[user]
            want = caps[user] - used(user) - quantity if ok else None
            expect(inv.add_item_by(user, base, quantity), want,
                   f"add_item_by({user}, {base}, {quantity}) at step {step}")
            if ok:
                items[base] = [quantity, user]
        elif roll < 0.44:
            source = rng.choice(sorted(items)) if items and rng.random() < 0.8 else base
            target = rng.choice(bases) + (".packed" if source.endswith(".packed") else "")
            ok = source in items and target not in items
            if ok:
                quantity, owner = items[source]
                ok = owner == "admin" or used(owner) + quantity <= caps[owner]
            expect(inv.copy_item(source, target), ok,
                   f"copy_item({source}, {target}) at step {step}")
            if ok:
                items[target] = list(items[source])
        elif roll < 0.52:
            capacity = rng.randrange(0, 400)
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
        elif roll < 0.68:
            name = rng.choice(sorted(items)) if items and rng.random() < 0.8 else base
            item = items.get(name)
            ok = (user in caps and item is not None and item[1] == user
                  and not name.endswith(".packed") and name + ".packed" not in items)
            want = None
            if ok:
                del items[name]
                items[name + ".packed"] = [item[0] // 2, user]
                want = caps[user] - used(user)
            expect(inv.pack_item(user, name), want, f"pack_item({user}, {name}) at step {step}")
        elif roll < 0.84:
            packed = [n[:-len(".packed")] for n in sorted(items) if n.endswith(".packed")]
            name = rng.choice(packed) if packed and rng.random() < 0.8 else base
            item = items.get(name + ".packed")
            ok = (user in caps and item is not None and item[1] == user
                  and name not in items and used(user) + item[0] <= caps[user])
            want = None
            if ok:
                del items[name + ".packed"]
                items[name] = [item[0] * 2, user]
                want = caps[user] - used(user)
            expect(inv.unpack_item(user, name), want,
                   f"unpack_item({user}, {name}) at step {step}")
        elif roll < 0.92:
            name = rng.choice(sorted(items) + [base])
            expect(inv.get_item_quantity(name), items[name][0] if name in items else None,
                   f"get_item_quantity({name}) at step {step}")
        else:
            prefix = rng.choice(["", "/a", "/b", "/"])
            suffix = rng.choice(["", ".packed", "a", "d"])
            matches = sorted((n for n in items if n.startswith(prefix) and n.endswith(suffix)),
                             key=lambda n: (-items[n][0], n))
            expect(inv.find_items(prefix, suffix), [f"{n}({items[n][0]})" for n in matches],
                   f"find_items({prefix!r}, {suffix!r}) at step {step}")
