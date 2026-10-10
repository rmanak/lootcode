class WorkerTimeTracker:
    """Badge-in / badge-out records for an office.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: office attendance ---------------------------------------

    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        pass

    def register(self, worker_id: str, timestamp: int) -> bool:
        pass

    def get_total_time(self, worker_id: str) -> int | None:
        pass

    # --- Level 2: ranking by time -----------------------------------------

    def top_n_workers(self, n: int, position: str) -> list[str]:
        pass

    # --- Level 3: promotions and salary -----------------------------------

    def promote(self, worker_id: str, new_position: str,
                new_compensation: int) -> bool:
        pass

    def calc_salary(self, worker_id: str, start_timestamp: int,
                    end_timestamp: int) -> int | None:
        pass

    # --- Level 4: double-pay periods --------------------------------------

    def set_double_pay(self, start_timestamp: int, end_timestamp: int) -> None:
        pass
