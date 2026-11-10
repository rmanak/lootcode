class ParcelTracker:
    """Tracks scan events per parcel, and the couriers carrying them.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: recording events ----------------------------------------

    def record_event(self, parcel_id: str, event_type: str, count: int) -> int:
        pass

    def get_event_count(self, parcel_id: str, event_type: str) -> int | None:
        pass

    def remove_event(self, parcel_id: str, event_type: str) -> bool:
        pass

    # --- Level 2: the busiest parcels -------------------------------------

    def top_parcels(self, n: int) -> list[str]:
        pass

    # --- Level 3: couriers ------------------------------------------------

    def assign_courier(self, parcel_id: str, courier_id: str) -> bool:
        pass

    def record_courier_event(self, courier_id: str, parcel_id: str,
                             event_type: str, count: int) -> int | None:
        pass

    def get_courier_parcels(self, courier_id: str) -> list[str]:
        pass

    # --- Level 4: undo and sign-out ---------------------------------------

    def undo_assignment(self, parcel_id: str) -> bool:
        pass

    def sign_out(self, courier_id: str) -> int:
        pass
