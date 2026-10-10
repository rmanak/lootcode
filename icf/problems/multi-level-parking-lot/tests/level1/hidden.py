"""Level 1 — levels and parking (hidden cases)."""
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


@case("a refused add_level does not change the existing level")
def failed_add_is_inert(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "M")
    expect(lot.add_level(2, "G", "RRRR"), False)
    expect(lot.park(3, "A", "car"), None, "G is still one motorcycle spot")
    expect(lot.park(4, "M", "motorcycle"), "G-0")


@case("a motorcycle falls back to the first regular spot, searching levels in order")
def motorcycle_fallback_order(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "M")
    lot.add_level(2, "P1", "RR")
    lot.add_level(3, "P2", "M")
    expect(lot.park(4, "m1", "motorcycle"), "G-0")
    expect(lot.park(5, "m2", "motorcycle"), "P2-0", "a motorcycle spot on a later level first")
    expect(lot.park(6, "m3", "motorcycle"), "P1-0", "then the first regular spot")


@case("a vehicle that returns gets the first free spot, not its old one")
def return_gets_first_free(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "RRR")
    lot.park(2, "A", "car")
    lot.park(3, "B", "car")
    lot.unpark(4, "A")
    lot.unpark(5, "B")
    expect(lot.park(6, "B", "car"), "G-0")
    expect(lot.find_vehicle(7, "B"), "G-0")


@case("a parked motorcycle cannot park again as a car")
def same_plate_other_type(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "MR")
    expect(lot.park(2, "X", "motorcycle"), "G-0")
    expect(lot.park(3, "X", "car"), None)
    expect(lot.find_vehicle(4, "X"), "G-0")
    expect(lot.park(5, "Y", "car"), "G-1", "the regular spot is still free")


@case("a level added later is used once earlier levels are full")
def level_added_later(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "G", "R")
    lot.park(2, "A", "car")
    expect(lot.park(3, "B", "car"), None)
    lot.add_level(4, "P1", "MR")
    expect(lot.park(5, "B", "car"), "P1-1")


@case("a single level with many spots fills left to right")
def long_level(ParkingLot):
    lot = ParkingLot()
    lot.add_level(1, "L", "R" * 300)
    for i in range(300):
        expect(lot.park(2 + i, f"c{i}", "car"), f"L-{i}")
    expect(lot.park(400, "extra", "car"), None)
    expect(lot.unpark(401, "c150"), "L-150")
    expect(lot.park(402, "extra", "car"), "L-150")


@case("a random workload of motorcycles and cars matches a reference model")
def fuzz_level1(ParkingLot):
    for seed in (1, 2, 3):
        replay(ParkingLot(), Model(),
               workload(seed, 400, ["add_level", "park", "park", "park", "unpark",
                                    "unpark", "find_vehicle"], ["motorcycle", "car"]))
