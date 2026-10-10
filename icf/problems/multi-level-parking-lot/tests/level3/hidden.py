"""Level 3 — buses (hidden cases)."""
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


@case("exactly five free regular spots in a row fit a bus; four do not")
def bus_needs_exactly_five(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "A", "RRRR")
    expect(lot.park(2, "bus", "bus"), None)
    lot.add_level(3, "B", "RRRRR")
    expect(lot.park(4, "bus", "bus"), "B-0")
    expect(lot.count_free(5, "B", "R"), 0)


@case("a row of spots never continues onto the next level")
def bus_row_per_level(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "A", "RRR")
    lot.add_level(2, "B", "RRR")
    expect(lot.park(3, "bus", "bus"), None)
    expect(lot.park(4, "car", "car"), "A-0", "the refused bus took no spot")


@case("an occupied spot in the middle breaks the row")
def occupied_breaks_row(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRRRRRRRR")
    lot.park(2, "c0", "car")
    lot.park(3, "c1", "car")
    lot.park(4, "c2", "car")
    lot.unpark(5, "c0")
    lot.unpark(6, "c2")
    # free: 0, 2..8 -> the first row of five starts at 2
    expect(lot.park(7, "bus", "bus"), "G-2")
    expect(lot.list_level(8, "G"), ["c1", "bus"])


@case("a bus takes the first level with room, even if a later level is emptier")
def bus_first_level(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRRRRM")
    lot.add_level(2, "P1", "RRRRRRRRRR")
    expect(lot.park(3, "b1", "bus"), "G-0")
    expect(lot.park(4, "b2", "bus"), "P1-0")
    expect(lot.park(5, "b3", "bus"), "P1-5")
    expect(lot.park(6, "b4", "bus"), None)


@case("after a bus leaves all five spots are free and counted again")
def bus_unpark_frees_all(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRRRRR")
    lot.park(2, "bus", "bus")
    expect(lot.top_levels(3, 1), ["G(1)"])
    expect(lot.find_vehicle(4, "bus"), "G-0")
    expect(lot.unpark(5, "bus"), "G-0")
    expect(lot.top_levels(6, 1), ["G(6)"])
    expect(lot.park(7, "car", "car"), "G-0")
    expect(lot.park(8, "bus", "bus"), "G-1", "spots 1-5 are a row of five")


@case("a parked bus plate cannot park again, and a bus never uses motorcycle spots")
def bus_rules(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MMMMMRRRRR")
    expect(lot.park(2, "b", "bus"), "G-5")
    expect(lot.park(3, "b", "car"), None)
    expect(lot.count_free(4, "G", "M"), 5)


@case("list_level is empty for an empty level and None for an unknown one")
def list_level_edges(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RM")
    expect(lot.list_level(2, "G"), [])
    expect(lot.list_level(3, "nope"), None)
    lot.park(4, "m", "motorcycle")
    lot.park(5, "c", "car")
    expect(lot.list_level(6, "G"), ["c", "m"], "by spot position, not arrival")


@case("a random workload with buses matches a reference model")
def fuzz_level3(ParkingLot):
    for seed in (21, 22, 23, 24):
        replay(ParkingLot(), Model(),
               workload(seed, 500, ["add_level", "park", "park", "park", "unpark",
                                    "unpark", "find_vehicle", "count_free",
                                    "top_levels", "list_level"],
                        ["motorcycle", "car", "bus", "bus"]))
