class ParkingLot:
    """A multi-level parking lot.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: levels and parking --------------------------------------

    def add_level(self, timestamp: int, level_id: str, layout: str) -> bool:
        pass

    def park(self, timestamp: int, plate: str, vehicle_type: str) -> str | None:
        pass

    def unpark(self, timestamp: int, plate: str) -> str | None:
        pass

    def find_vehicle(self, timestamp: int, plate: str) -> str | None:
        pass

    # --- Level 2: free spots ----------------------------------------------

    def count_free(self, timestamp: int, level_id: str, spot_type: str) -> int | None:
        pass

    def top_levels(self, timestamp: int, n: int) -> list[str]:
        pass

    # --- Level 3: buses ---------------------------------------------------

    def list_level(self, timestamp: int, level_id: str) -> list[str] | None:
        pass

    # --- Level 4: fees ----------------------------------------------------

    def set_rate(self, timestamp: int, vehicle_type: str, rate: int) -> None:
        pass

    def get_fee(self, timestamp: int, plate: str) -> int | None:
        pass

    def get_history(self, timestamp: int, plate: str) -> list[str]:
        pass

    def get_revenue(self, timestamp: int) -> int:
        pass
