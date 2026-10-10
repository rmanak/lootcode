"""Level 2 — free spots (hidden cases)."""
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


@case("count_free counts one spot type on one level and follows parking")
def count_free_tracks(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MMRRR")
    expect(lot.count_free(2, "G", "M"), 2)
    expect(lot.count_free(3, "G", "R"), 3)
    lot.park(4, "m", "motorcycle")
    lot.park(5, "c", "car")
    expect(lot.count_free(6, "G", "M"), 1)
    expect(lot.count_free(7, "G", "R"), 2)
    lot.unpark(8, "c")
    expect(lot.count_free(9, "G", "R"), 3)


@case("a motorcycle on a regular spot lowers the regular count, not the motorcycle count")
def fallback_counts_regular(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MR")
    lot.park(2, "m1", "motorcycle")
    lot.park(3, "m2", "motorcycle")
    expect(lot.count_free(4, "G", "M"), 0)
    expect(lot.count_free(5, "G", "R"), 0)


@case("a full level still appears in top_levels with a count of 0")
def full_level_listed(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "A", "R")
    lot.add_level(2, "B", "RR")
    lot.park(3, "x", "car")
    expect(lot.top_levels(4, 5), ["B(2)", "A(0)"])


@case("ties in top_levels are broken by ordinary string order of the level id")
def tie_break_string_order(ParkingLot):
    lot = ParkingLot()
    for i, name in enumerate(["P2", "P10", "G", "B1"], start=1):
        lot.add_level(i, name, "RR")
    expect(lot.top_levels(10, 4), ["B1(2)", "G(2)", "P10(2)", "P2(2)"])
    expect(lot.top_levels(11, 1), ["B1(2)"])


@case("top_levels on an empty lot is empty")
def top_levels_empty(ParkingLot):
    lot = ParkingLot()
    expect(lot.top_levels(1, 3), [])
    lot.add_level(2, "G", "M")
    expect(lot.top_levels(3, 3), ["G(1)"])


@case("a random workload with counting and ranking matches a reference model")
def fuzz_level2(ParkingLot):
    for seed in (11, 12, 13):
        replay(ParkingLot(), Model(),
               workload(seed, 400, ["add_level", "park", "park", "park", "unpark",
                                    "unpark", "find_vehicle", "count_free",
                                    "top_levels"], ["motorcycle", "car"]))
