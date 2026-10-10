"""Checkpoint: the reference solution after levels 1-3 (no fees yet)."""

from dataclasses import dataclass, field

BUS_LENGTH = 5


@dataclass(slots=True)
class Spot:
    spot_id: str
    kind: str                      # "M" (motorcycle) or "R" (regular)
    plate: str | None = None       # who is parked here, if anyone

    @property
    def free(self) -> bool:
        return self.plate is None


@dataclass(slots=True)
class Level:
    level_id: str
    spots: list[Spot]

    def free_count(self, kind: str | None = None) -> int:
        return sum(1 for spot in self.spots
                   if spot.free and (kind is None or spot.kind == kind))

    def first_free(self, kind: str) -> Spot | None:
        for spot in self.spots:
            if spot.free and spot.kind == kind:
                return spot
        return None

    def first_run(self, length: int) -> list[Spot] | None:
        """The leftmost `length` consecutive free regular spots, if any."""
        run: list[Spot] = []
        for spot in self.spots:
            if spot.free and spot.kind == "R":
                run.append(spot)
                if len(run) == length:
                    return run
            else:
                run = []
        return None


@dataclass(slots=True)
class Stay:
    """One vehicle's visit, from `park` to `unpark`."""

    plate: str
    spots: list[Spot]
    level_id: str
    started_at: int
    index: int = field(default=0)  # position of the first spot on its level

    @property
    def spot_id(self) -> str:
        return self.spots[0].spot_id

class ParkingLot:
    def __init__(self) -> None:
        self._levels: dict[str, Level] = {}      # insertion order = search order
        self._parked: dict[str, Stay] = {}

    # --- helpers -----------------------------------------------------------

    def _first_free(self, kind: str) -> tuple[Level, Spot] | None:
        for level in self._levels.values():
            spot = level.first_free(kind)
            if spot is not None:
                return level, spot
        return None

    def _find_spots(self, vehicle_type: str) -> tuple[Level, list[Spot]] | None:
        if vehicle_type == "bus":
            for level in self._levels.values():
                run = level.first_run(BUS_LENGTH)
                if run is not None:
                    return level, run
            return None
        kinds = ["M", "R"] if vehicle_type == "motorcycle" else ["R"]
        for kind in kinds:
            found = self._first_free(kind)
            if found is not None:
                return found[0], [found[1]]
        return None

    # --- Level 1 -----------------------------------------------------------

    def add_level(self, timestamp: int, level_id: str, layout: str) -> bool:
        if level_id in self._levels:
            return False
        spots = [Spot(f"{level_id}-{i}", kind) for i, kind in enumerate(layout)]
        self._levels[level_id] = Level(level_id, spots)
        return True

    def park(self, timestamp: int, plate: str, vehicle_type: str) -> str | None:
        if plate in self._parked:
            return None
        found = self._find_spots(vehicle_type)
        if found is None:
            return None
        level, spots = found
        for spot in spots:
            spot.plate = plate
        stay = Stay(plate, spots, level.level_id, timestamp,
                    level.spots.index(spots[0]))
        self._parked[plate] = stay
        return stay.spot_id

    def unpark(self, timestamp: int, plate: str) -> str | None:
        stay = self._parked.pop(plate, None)
        if stay is None:
            return None
        for spot in stay.spots:
            spot.plate = None
        return stay.spot_id

    def find_vehicle(self, timestamp: int, plate: str) -> str | None:
        stay = self._parked.get(plate)
        return None if stay is None else stay.spot_id

    # --- Level 2 -----------------------------------------------------------

    def count_free(self, timestamp: int, level_id: str, spot_type: str) -> int | None:
        level = self._levels.get(level_id)
        return None if level is None else level.free_count(spot_type)

    def top_levels(self, timestamp: int, n: int) -> list[str]:
        ranked = sorted(self._levels.values(),
                        key=lambda level: (-level.free_count(), level.level_id))
        return [f"{level.level_id}({level.free_count()})" for level in ranked[:n]]

    # --- Level 3 -----------------------------------------------------------

    def list_level(self, timestamp: int, level_id: str) -> list[str] | None:
        if level_id not in self._levels:
            return None
        here = [stay for stay in self._parked.values() if stay.level_id == level_id]
        return [stay.plate for stay in sorted(here, key=lambda stay: stay.index)]
