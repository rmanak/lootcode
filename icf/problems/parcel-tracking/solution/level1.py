"""Checkpoint: the reference solution after level 1 only.

The later levels' methods are removed; what remains is enough to pass
levels 1-1 and to fail level 2."""

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

    # --- Level 3 -----------------------------------------------------------

    # --- Level 4 -----------------------------------------------------------

