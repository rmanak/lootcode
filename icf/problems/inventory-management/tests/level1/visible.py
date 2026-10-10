"""Level 1 — items (visible cases)."""
from icf_testkit import case, expect


@case("add_item stores an item and get_item_quantity reads it back")
def add_and_read(InventoryManager):
    inv = InventoryManager()
    expect(inv.add_item("/warehouse/sectionA/item1", 20), True)
    expect(inv.get_item_quantity("/warehouse/sectionA/item1"), 20)


@case("an item name can be added only once")
def add_once(InventoryManager):
    inv = InventoryManager()
    expect(inv.add_item("/bolts", 20), True)
    expect(inv.add_item("/bolts", 35), False)
    expect(inv.get_item_quantity("/bolts"), 20, "the quantity did not change")


@case("get_item_quantity returns None for an unknown item")
def unknown_item(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/bolts", 20)
    expect(inv.get_item_quantity("/bolts"), 20)
    expect(inv.get_item_quantity("/nuts"), None)


@case("copy_item creates a new item with the same quantity")
def copy_creates_item(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/a/bolts", 20)
    expect(inv.copy_item("/a/bolts", "/b/bolts"), True)
    expect(inv.get_item_quantity("/b/bolts"), 20)
    expect(inv.get_item_quantity("/a/bolts"), 20, "the original is still there")


@case("copy_item is refused when the source is missing or the target already exists")
def copy_refused(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/warehouse/sectionA/item1", 20)
    expect(inv.copy_item("/not-existing.item", "/warehouse/sectionB/item1"), False)
    expect(inv.copy_item("/warehouse/sectionA/item1", "/warehouse/sectionB/item1"), True)
    expect(inv.add_item("/warehouse/sectionB/item1", 35), False)
    expect(inv.copy_item("/warehouse/sectionB/item1", "/warehouse/sectionA/item1"), False)
    expect(inv.get_item_quantity("/warehouse/sectionB/item1"), 20)
