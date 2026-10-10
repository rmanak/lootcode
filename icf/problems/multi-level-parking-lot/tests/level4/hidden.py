"""Level 4 — fees (hidden cases)."""
import random

from icf_testkit import case, expect


class Model:
    """A deliberately naive reference: one flat occupancy map, rescanned every time."""

    HOUR = 3_600_000

    def __init__(self):
        self.order = []            # level ids in added order
        self.layout = {}           # level id -> layout string
        self.occ = {}              # (level id, index) -> plate
        self.where = {}            # plate -> [level id, index, size, start, rate]
        self.rates = {}
        self.history = {}
        self.revenue = 0

    def add_level(self, ts, level_id, layout):
        if level_id in self.layout:
            return False
        self.order.append(level_id)
        self.layout[level_id] = layout
        return True

    def _free(self, lv, i):
        return (lv, i) not in self.occ

    def park(self, ts, plate, vtype):
        if plate in self.where:
            return None
        choice = None
        if vtype == "bus":
            for lv in self.order:
                lay = self.layout[lv]
                for i in range(len(lay) - 4):
                    if all(lay[j] == "R" and self._free(lv, j) for j in range(i, i + 5)):
                        choice = (lv, i, 5)
                        break
                if choice:
                    break
        else:
            kinds = "MR" if vtype == "motorcycle" else "R"
            for kind in kinds:
                for lv in self.order:
                    for i, k in enumerate(self.layout[lv]):
                        if k == kind and self._free(lv, i):
                            choice = (lv, i, 1)
                            break
                    if choice:
                        break
                if choice:
                    break
        if choice is None:
            return None
        lv, i, size = choice
        for j in range(i, i + size):
            self.occ[(lv, j)] = plate
        self.where[plate] = [lv, i, size, ts, self.rates.get(vtype, 0)]
        return f"{lv}-{i}"

    def _fee(self, plate, ts):
        lv, i, size, start, rate = self.where[plate]
        hours = max(1, (ts - start + self.HOUR - 1) // self.HOUR)
        return hours * rate

    def unpark(self, ts, plate):
        if plate not in self.where:
            return None
        fee = self._fee(plate, ts)
        lv, i, size, start, rate = self.where.pop(plate)
        for j in range(i, i + size):
            del self.occ[(lv, j)]
        self.revenue += fee
        self.history.setdefault(plate, []).append(f"{lv}-{i}({fee})")
        return f"{lv}-{i}"

    def find_vehicle(self, ts, plate):
        if plate not in self.where:
            return None
        return f"{self.where[plate][0]}-{self.where[plate][1]}"

    def count_free(self, ts, level_id, kind):
        if level_id not in self.layout:
            return None
        return sum(1 for i, k in enumerate(self.layout[level_id])
                   if k == kind and self._free(level_id, i))

    def top_levels(self, ts, n):
        free = {lv: sum(1 for i in range(len(self.layout[lv])) if self._free(lv, i))
                for lv in self.order}
        ranked = sorted(self.order, key=lambda lv: (-free[lv], lv))
        return [f"{lv}({free[lv]})" for lv in ranked[:n]]

    def list_level(self, ts, level_id):
        if level_id not in self.layout:
            return None
        seen = []
        for i in range(len(self.layout[level_id])):
            plate = self.occ.get((level_id, i))
            if plate is not None and plate not in seen:
                seen.append(plate)
        return seen

    def set_rate(self, ts, vtype, rate):
        self.rates[vtype] = rate

    def get_fee(self, ts, plate):
        return None if plate not in self.where else self._fee(plate, ts)

    def get_history(self, ts, plate):
        return list(self.history.get(plate, []))

    def get_revenue(self, ts):
        return self.revenue


def replay(lot, model, calls):
    """Run the same calls on the solver's lot and the model, comparing each result."""
    for name, args in calls:
        expect(getattr(lot, name)(*args), getattr(model, name)(*args),
               f"{name}{tuple(args)}")


def workload(seed, steps, ops, vtypes, step_ms=1):
    """A random call sequence using only `ops`; timestamps strictly increase."""
    rng = random.Random(seed)
    plates = [f"V{i}" for i in range(12)]
    levels = ["G", "P1", "P2", "B1"]
    layouts = ["MRRRRRRR", "RRRRRRRRRR", "MMRR", "RRMRRRRRRRRR", "R", "MRRRRRMRRRRR"]
    calls, ts = [], 0
    for _ in range(steps):
        ts += rng.randint(1, step_ms)
        op = rng.choice(ops)
        if op == "add_level":
            args = [ts, rng.choice(levels), rng.choice(layouts)]
        elif op == "park":
            args = [ts, rng.choice(plates), rng.choice(vtypes)]
        elif op in ("unpark", "find_vehicle", "get_fee", "get_history"):
            args = [ts, rng.choice(plates)]
        elif op == "count_free":
            args = [ts, rng.choice(levels + ["X9"]), rng.choice("MR")]
        elif op == "top_levels":
            args = [ts, rng.randint(0, 5)]
        elif op == "list_level":
            args = [ts, rng.choice(levels + ["X9"])]
        elif op == "set_rate":
            args = [ts, rng.choice(["motorcycle", "car", "bus"]), rng.randint(0, 20)]
        else:  # get_revenue
            args = [ts]
        calls.append((op, args))
    return calls


HOUR = 3_600_000


@case("the fee is per started hour, and exactly one hour is one hour")
def fee_boundary(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.set_rate(2, "car", 7)
    lot.park(10, "c", "car")
    expect(lot.get_fee(11, "c"), 7, "a moment in is already 1 hour")
    expect(lot.get_fee(10 + HOUR, "c"), 7)
    expect(lot.get_fee(10 + HOUR + 1, "c"), 14)
    expect(lot.get_fee(10 + 5 * HOUR, "c"), 35)
    expect(lot.unpark(10 + 5 * HOUR + 1, "c"), "G-0")
    expect(lot.get_history(10 + 5 * HOUR + 2, "c"), ["G-0(42)"])


@case("rates are per vehicle type and default to 0")
def rates_per_type(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MRRRRRR")
    lot.set_rate(2, "bus", 50)
    lot.park(3, "m", "motorcycle")
    lot.park(4, "b", "bus")
    lot.unpark(5, "m")
    lot.unpark(6, "b")
    expect(lot.get_history(7, "m"), ["G-0(0)"])
    expect(lot.get_history(8, "b"), ["G-1(50)"], "a bus is recorded at its leftmost spot")
    expect(lot.get_revenue(9), 50)


@case("a rate change does not affect vehicles already parked")
def rate_locked_at_arrival(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RR")
    lot.set_rate(2, "car", 3)
    lot.park(3, "early", "car")
    lot.set_rate(4, "car", 100)
    lot.park(5, "late", "car")
    expect(lot.get_fee(6, "early"), 3)
    expect(lot.get_fee(7, "late"), 100)
    lot.set_rate(8, "car", 0)
    expect(lot.unpark(9, "late"), "G-1")
    expect(lot.get_revenue(10), 100)


@case("a stay in progress is not in the history or the revenue")
def in_progress_not_counted(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.set_rate(2, "car", 5)
    lot.park(3, "c", "car")
    expect(lot.get_history(4, "c"), [])
    expect(lot.get_revenue(5), 0)
    expect(lot.get_fee(6, "c"), 5)
    expect(lot.get_fee(7, "ghost"), None)


@case("refused park and unpark calls charge nothing")
def refusals_charge_nothing(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.set_rate(2, "car", 9)
    lot.park(3, "a", "car")
    expect(lot.park(4, "b", "car"), None)
    expect(lot.park(5, "a", "car"), None)
    expect(lot.unpark(6, "b"), None)
    expect(lot.get_history(7, "b"), [])
    expect(lot.unpark(8, "a"), "G-0")
    expect(lot.get_revenue(9), 9)


@case("each stay is charged separately and listed oldest first")
def many_stays(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RR")
    lot.set_rate(2, "car", 2)
    ts = 10
    for hours in (1, 3, 2):
        lot.park(ts, "c", "car")
        ts += hours * HOUR
        lot.unpark(ts, "c")
        ts += 1
    expect(lot.get_history(ts, "c"), ["G-0(2)", "G-0(6)", "G-0(4)"])
    expect(lot.get_revenue(ts + 1), 12)


@case("the history belongs to the plate, whatever the vehicle type")
def history_by_plate(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MRRRRR")
    lot.set_rate(2, "motorcycle", 1)
    lot.set_rate(3, "car", 2)
    lot.park(4, "X", "motorcycle")
    lot.unpark(5, "X")
    lot.park(6, "X", "car")
    lot.unpark(7, "X")
    expect(lot.get_history(8, "X"), ["G-0(1)", "G-1(2)"])


@case("a random workload with fees matches a reference model")
def fuzz_level4(ParkingLot):
    for seed in (31, 32, 33, 34):
        replay(ParkingLot(), Model(),
               workload(seed, 500, ["add_level", "add_level", "park", "park", "park",
                                    "unpark", "unpark", "find_vehicle", "count_free",
                                    "top_levels", "list_level", "set_rate", "get_fee",
                                    "get_history", "get_revenue"],
                        ["motorcycle", "car", "bus"], step_ms=2 * HOUR))
