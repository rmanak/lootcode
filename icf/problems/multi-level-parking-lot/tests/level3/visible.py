"""Level 3 — buses (visible cases)."""
from icf_testkit import case, expect


@case("a bus takes five regular spots in a row and reports the leftmost")
def bus_parks(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRRRRR")
    expect(lot.park(2, "bus", "bus"), "G-0")
    expect(lot.count_free(3, "G", "R"), 1)
    expect(lot.find_vehicle(4, "bus"), "G-0")


@case("a motorcycle spot breaks a row of regular spots")
def motorcycle_spot_breaks_row(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRRMRRRRR")
    expect(lot.park(2, "bus", "bus"), "G-4")


@case("a bus goes to the next level when this one has no row of five")
def bus_next_level(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRRR")
    lot.add_level(2, "P1", "RRRRR")
    expect(lot.park(3, "bus", "bus"), "P1-0")
    expect(lot.park(4, "bus2", "bus"), None, "no room left for a second bus")


@case("unpark frees all five spots of a bus")
def bus_unpark(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRRRR")
    lot.park(2, "bus", "bus")
    expect(lot.park(3, "car", "car"), None)
    expect(lot.unpark(4, "bus"), "G-0")
    expect(lot.count_free(5, "G", "R"), 5)


@case("list_level lists plates by spot position, with a bus listed once")
def list_level_order(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MRRRRRR")
    lot.park(2, "c", "car")
    lot.park(3, "bus", "bus")
    lot.unpark(4, "c")
    lot.park(5, "m", "motorcycle")
    expect(lot.list_level(6, "G"), ["m", "bus"])
    expect(lot.list_level(7, "nope"), None)
