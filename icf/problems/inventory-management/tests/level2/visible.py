"""Level 2 — finding items (visible cases)."""
from icf_testkit import case, expect


@case("find_items lists matching items, largest quantity first")
def largest_first(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/warehouse/sectionX/itemA", 50)
    inv.add_item("/warehouse/itemB", 25)
    inv.add_item("/warehouse/sectionY/itemC", 30)
    inv.add_item("/storage/itemD", 99)
    expect(inv.find_items("/warehouse/", ""),
           ["/warehouse/sectionX/itemA(50)", "/warehouse/sectionY/itemC(30)",
            "/warehouse/itemB(25)"])


@case("items with the same quantity are ordered by name")
def ties_by_name(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/warehouse/sectionY/itemC", 30)
    inv.copy_item("/warehouse/sectionY/itemC", "/warehouse/sectionZ/itemC")
    inv.add_item("/warehouse/sectionA/itemC", 30)
    expect(inv.find_items("/warehouse/section", "itemC"),
           ["/warehouse/sectionA/itemC(30)", "/warehouse/sectionY/itemC(30)",
            "/warehouse/sectionZ/itemC(30)"])


@case("a search that matches nothing returns an empty list")
def no_match(InventoryManager):
    inv = InventoryManager()
    inv.add_item("/warehouse/itemB", 25)
    expect(inv.find_items("/warehouse", "itemB"), ["/warehouse/itemB(25)"])
    expect(inv.find_items("/warehouse", "itemX"), [])
    expect(inv.find_items("/sectionY", "itemB"), [], "the name must start with the prefix")
