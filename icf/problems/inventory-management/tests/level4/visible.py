"""Level 4 — packing items (visible cases)."""
from icf_testkit import case, expect


@case("pack_item replaces an item with a packed item of half the quantity")
def pack_halves(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    expect(inv.add_item_by("ana", "/a", 400), 600)
    expect(inv.pack_item("ana", "/a"), 800)
    expect(inv.get_item_quantity("/a"), None)
    expect(inv.get_item_quantity("/a.packed"), 200)


@case("unpack_item restores the original item")
def unpack_restores(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    inv.add_item_by("ana", "/a", 400)
    inv.pack_item("ana", "/a")
    expect(inv.unpack_item("ana", "/a"), 600)
    expect(inv.get_item_quantity("/a"), 400)
    expect(inv.get_item_quantity("/a.packed"), None)


@case("packing is refused for an unknown user, a missing item, or someone else's item")
def pack_refused(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 100)
    inv.add_user("ben", 100)
    inv.add_item_by("ana", "/a", 40)
    expect(inv.pack_item("ghost", "/a"), None)
    expect(inv.pack_item("ana", "/zzz"), None)
    expect(inv.pack_item("ben", "/a"), None)
    expect(inv.pack_item("ana", "/a"), 80)


@case("unpacking is refused when the unpacked item would not fit")
def unpack_does_not_fit(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    inv.add_item_by("ana", "/a", 800)
    expect(inv.pack_item("ana", "/a"), 600)
    expect(inv.add_item_by("ana", "/b", 500), 100)
    expect(inv.unpack_item("ana", "/a"), None, "it would need 400 more units")
    expect(inv.get_item_quantity("/a.packed"), 400, "the packed item is untouched")
    expect(inv.update_capacity("ana", 1300), 0)
    expect(inv.unpack_item("ana", "/a"), 0)


@case("unpacking is refused while an item with the original name exists")
def unpack_name_taken(InventoryManager):
    inv = InventoryManager()
    inv.add_user("ana", 1000)
    inv.add_item_by("ana", "/a", 100)
    expect(inv.pack_item("ana", "/a"), 950)
    expect(inv.add_item_by("ana", "/a", 10), 940)
    expect(inv.unpack_item("ana", "/a"), None)
    expect(inv.get_item_quantity("/a"), 10)
    expect(inv.get_item_quantity("/a.packed"), 50)
