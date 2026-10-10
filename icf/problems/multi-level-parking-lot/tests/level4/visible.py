"""Level 4 — fees (visible cases)."""
from icf_testkit import case, expect

HOUR = 3_600_000


@case("get_fee charges each started hour at the rate for the vehicle type")
def fee_by_started_hour(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.set_rate(2, "car", 4)
    lot.park(3, "c", "car")
    expect(lot.get_fee(4, "c"), 4, "under an hour is 1 hour")
    expect(lot.get_fee(3 + HOUR, "c"), 4, "exactly an hour is 1 hour")
    expect(lot.get_fee(3 + HOUR + 1, "c"), 8, "just over is 2 hours")


@case("a vehicle that parked before any rate was set parks for free")
def default_rate_zero(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RR")
    lot.park(2, "free", "car")
    lot.set_rate(3, "car", 10)
    expect(lot.get_fee(4, "free"), 0)
    expect(lot.park(5, "paid", "car"), "G-1")
    expect(lot.get_fee(6, "paid"), 10)


@case("unpark records the stay in the history and adds its fee to the revenue")
def unpark_records(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MR")
    lot.set_rate(2, "motorcycle", 1)
    lot.set_rate(3, "car", 3)
    lot.park(4, "m", "motorcycle")
    lot.park(5, "c", "car")
    lot.unpark(6, "m")
    lot.unpark(7 + 2 * HOUR, "c")
    expect(lot.get_history(8 + 2 * HOUR, "c"), ["G-1(9)"])
    expect(lot.get_history(9 + 2 * HOUR, "m"), ["G-0(1)"])
    expect(lot.get_revenue(10 + 2 * HOUR), 10)


@case("changing a rate does not change what a parked vehicle pays")
def rate_locked(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.set_rate(2, "car", 5)
    lot.park(3, "c", "car")
    lot.set_rate(4, "car", 50)
    expect(lot.get_fee(5, "c"), 5)


@case("get_history is empty for a vehicle with no finished stay")
def empty_history(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.park(2, "c", "car")
    expect(lot.get_history(3, "c"), [])
    expect(lot.get_history(4, "ghost"), [])
    expect(lot.get_revenue(5), 0)
    expect(lot.find_vehicle(6, "c"), "G-0")
