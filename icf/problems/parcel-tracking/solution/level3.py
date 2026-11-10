"""Checkpoint: the reference solution after level 3 only.

The later levels' methods are removed; what remains is enough to pass
levels 1-3 and to fail level 4."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Parcel:
    parcel_id: str
    events: dict[str, int] = field(default_factory=dict)
    courier: str | None = None
    #: The courier before each change, oldest first (None = unassigned).
    previous_couriers: list[str | None] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(self.events.values())

    def change_courier(self, courier: str | None) -> None:
        self.previous_couriers.append(self.courier)
        self.courier = courier


class ParcelTracker:
    def __init__(self) -> None:
        self._parcels: dict[str, Parcel] = {}

    # --- Level 1 -----------------------------------------------------------

    def record_event(self, parcel_id: str, event_type: str, count: int) -> int:
        parcel = self._parcels.setdefault(parcel_id, Parcel(parcel_id))
        parcel.events[event_type] = parcel.events.get(event_type, 0) + count
        return parcel.events[event_type]

    def get_event_count(self, parcel_id: str, event_type: str) -> int | None:
        parcel = self._parcels.get(parcel_id)
        if parcel is None:
            return None
        return parcel.events.get(event_type)

    def remove_event(self, parcel_id: str, event_type: str) -> bool:
        parcel = self._parcels.get(parcel_id)
        if parcel is None or event_type not in parcel.events:
            return False
        del parcel.events[event_type]
        if not parcel.events:
            del self._parcels[parcel_id]
        return True

    # --- Level 2 -----------------------------------------------------------

    def top_parcels(self, n: int) -> list[str]:
        ranked = sorted(self._parcels.values(),
                        key=lambda parcel: (-parcel.total, parcel.parcel_id))
        return [f"{parcel.parcel_id}({parcel.total})" for parcel in ranked[:n]]

    # --- Level 3 -----------------------------------------------------------

    def assign_courier(self, parcel_id: str, courier_id: str) -> bool:
        parcel = self._parcels.get(parcel_id)
        if parcel is None or parcel.courier == courier_id:
            return False
        parcel.change_courier(courier_id)
        return True

    def record_courier_event(self, courier_id: str, parcel_id: str,
                             event_type: str, count: int) -> int | None:
        parcel = self._parcels.get(parcel_id)
        if parcel is None or parcel.courier != courier_id:
            return None
        return self.record_event(parcel_id, event_type, count)

    def get_courier_parcels(self, courier_id: str) -> list[str]:
        return sorted(parcel.parcel_id for parcel in self._parcels.values()
                      if parcel.courier == courier_id)

    # --- Level 4 -----------------------------------------------------------

