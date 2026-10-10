"""Checkpoint: the reference solution after level 1 only."""

from dataclasses import dataclass


@dataclass(slots=True)
class Spot:
    spot_id: str
    kind: str                      # "M" (motorcycle) or "R" (regular)
    plate: str | None = None


class ParkingLot:
    def __init__(self) -> None:
        self._levels: dict[str, list[Spot]] = {}   # insertion order = search order
        self._parked: dict[str, Spot] = {}

    def _first_free(self, kind: str) -> Spot | None:
        for spots in self._levels.values():
            for spot in spots:
                if spot.plate is None and spot.kind == kind:
                    return spot
        return None

    def add_level(self, timestamp: int, level_id: str, layout: str) -> bool:
        if level_id in self._levels:
            return False
        self._levels[level_id] = [Spot(f"{level_id}-{i}", kind)
                                  for i, kind in enumerate(layout)]
        return True

    def park(self, timestamp: int, plate: str, vehicle_type: str) -> str | None:
        if plate in self._parked:
            return None
        kinds = ["M", "R"] if vehicle_type == "motorcycle" else ["R"]
        for kind in kinds:
            spot = self._first_free(kind)
            if spot is not None:
                spot.plate = plate
                self._parked[plate] = spot
                return spot.spot_id
        return None

    def unpark(self, timestamp: int, plate: str) -> str | None:
        spot = self._parked.pop(plate, None)
        if spot is None:
            return None
        spot.plate = None
        return spot.spot_id

    def find_vehicle(self, timestamp: int, plate: str) -> str | None:
        spot = self._parked.get(plate)
        return None if spot is None else spot.spot_id
