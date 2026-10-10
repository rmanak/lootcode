"""Level 1 — levels and parking (visible cases)."""
from icf_testkit import case, expect


@case("a level is added once, and the second attempt with the same id is refused")
def add_level_once(ParkingLot):
    lot = ParkingLot()
    expect(lot.add_level(1, "G", "RR"), True)
    expect(lot.add_level(2, "G", "MMMM"), False, "the id is taken")
    expect(lot.park(3, "A", "car"), "G-0", "the original layout is kept")


@case("nothing can park before a level exists")
def park_without_levels(ParkingLot):
    lot = ParkingLot()
    expect(lot.park(1, "A", "car"), None)
    expect(lot.add_level(2, "G", "R"), True)
    expect(lot.park(3, "A", "car"), "G-0")


@case("a car takes the first free regular spot, and spot ids are level-index")
def car_first_regular(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "B1", "MRR")
    expect(lot.park(2, "A", "car"), "B1-1")
    expect(lot.park(3, "B", "car"), "B1-2")
    expect(lot.park(4, "C", "car"), None, "a car never uses a motorcycle spot")


@case("a motorcycle prefers a motorcycle spot on any level over a regular spot")
def motorcycle_prefers_m(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RR")
    lot.add_level(2, "P1", "RM")
    expect(lot.park(3, "M1", "motorcycle"), "P1-1")
    expect(lot.park(4, "M2", "motorcycle"), "G-0", "no motorcycle spot left")


@case("levels are searched in the order they were added")
def levels_in_added_order(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "Z", "R")
    lot.add_level(2, "A", "R")
    expect(lot.park(3, "car1", "car"), "Z-0")
    expect(lot.park(4, "car2", "car"), "A-0")


@case("unpark frees the spot and returns it; a vehicle not parked gives None")
def unpark_frees(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.park(2, "A", "car")
    expect(lot.park(3, "B", "car"), None, "the lot is full")
    expect(lot.unpark(4, "A"), "G-0")
    expect(lot.unpark(5, "A"), None, "A already left")
    expect(lot.park(6, "B", "car"), "G-0")


@case("find_vehicle reports the spot of a parked vehicle, or None")
def find_vehicle(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MR")
    lot.park(2, "A", "car")
    expect(lot.find_vehicle(3, "A"), "G-1")
    expect(lot.find_vehicle(4, "ghost"), None)


@case("a plate that is already parked cannot park again")
def no_double_park(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRR")
    expect(lot.park(2, "A", "car"), "G-0")
    expect(lot.park(3, "A", "car"), None)
    expect(lot.park(4, "B", "car"), "G-1", "the refused park took no spot")
