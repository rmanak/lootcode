"""Level 3 — users and capacity (visible cases)."""
from icf_testkit import case, expect


@case("a user can be added only once")
def add_user_once(InventoryManager):
    inv = InventoryManager()
    expect(inv.add_user("user1", 1500), True)
    expect(inv.add_user("user1", 1200), False)


@case("add_item_by returns the capacity the user has left")
def remaining_capacity(InventoryManager):
    inv = InventoryManager()
    inv.add_user("user1", 1500)
    expect(inv.add_item_by("user1", "/sectionA/itemBig", 600), 900)
    expect(inv.add_item_by("user1", "/itemMed", 400), 500)
    expect(inv.get_item_quantity("/itemMed"), 400)


@case("an item that does not fit is refused, and one that exactly fits is accepted")
def capacity_limit(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 500)
    expect(inv.add_item_by("u", "/a", 400), 100)
    expect(inv.add_item_by("u", "/b", 200), None, "only 100 units are left")
    expect(inv.add_item_by("u", "/c", 100), 0)
    expect(inv.get_item_quantity("/b"), None, "the refused item was not added")


@case("add_item_by is refused for an unknown user or a name that is taken")
def add_item_by_refused(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 100)
    inv.add_item("/taken", 5)
    expect(inv.add_item_by("ghost", "/x", 1), None)
    expect(inv.add_item_by("u", "/taken", 1), None)
    expect(inv.add_item_by("u", "/x", 1), 99)


@case("update_capacity removes the largest items until the rest fit")
def eviction(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 1200)
    inv.add_item_by("u", "/a", 300)
    inv.add_item_by("u", "/b", 400)
    inv.add_item_by("u", "/c", 400)
    inv.add_item_by("u", "/d", 100)
    expect(inv.update_capacity("u", 450), 2, "/b then /c: 1200 -> 800 -> 400")
    expect(inv.get_item_quantity("/b"), None)
    expect(inv.get_item_quantity("/c"), None)
    expect(inv.get_item_quantity("/a"), 300)
    expect(inv.get_item_quantity("/d"), 100)
    expect(inv.add_item_by("u", "/e", 50), 0)


@case("a copy belongs to the owner of the original and counts against their capacity")
def copy_keeps_owner(InventoryManager):
    inv = InventoryManager()
    inv.add_user("u", 500)
    expect(inv.add_item_by("u", "/x", 200), 300)
    expect(inv.copy_item("/x", "/y"), True)
    expect(inv.add_item_by("u", "/z", 101), None, "the copy used 200 of the 300 left")
    expect(inv.add_item_by("u", "/z", 100), 0)
