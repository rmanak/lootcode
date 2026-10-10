"""Level 2 — free spots (visible cases)."""
from icf_testkit import case, expect


@case("count_free counts the free spots of one type on one level")
def count_free_basic(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MRRR")
    lot.park(2, "c", "car")
    expect(lot.count_free(3, "G", "R"), 2)
    expect(lot.count_free(4, "G", "M"), 1)


@case("count_free on a level that does not exist returns None")
def count_free_missing(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    expect(lot.count_free(2, "G", "R"), 1)
    expect(lot.count_free(3, "P9", "R"), None)


@case("top_levels ranks levels by free spots of both types, most first")
def top_levels_ranking(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MR")
    lot.add_level(2, "P1", "MMRR")
    lot.add_level(3, "P2", "RRR")
    lot.park(4, "c", "car")
    expect(lot.top_levels(5, 3), ["P1(4)", "P2(3)", "G(1)"])


@case("tied levels are ordered by level id, and n caps the list")
def top_levels_ties(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "P1", "RR")
    lot.add_level(2, "G", "MR")
    lot.add_level(3, "B1", "R")
    expect(lot.top_levels(4, 2), ["G(2)", "P1(2)"])
    expect(lot.top_levels(5, 10), ["G(2)", "P1(2)", "B1(1)"])
    expect(lot.top_levels(6, 0), [])
