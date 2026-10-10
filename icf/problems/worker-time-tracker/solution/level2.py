"""Checkpoint: the reference solution after levels 1 and 2."""

from dataclasses import dataclass


@dataclass(slots=True)
class Worker:
    position: str
    compensation: int
    entered_at: int | None = None     # None when off the clock
    total: int = 0


class WorkerTimeTracker:
    def __init__(self) -> None:
        self._workers: dict[str, Worker] = {}

    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        if worker_id in self._workers:
            return False
        self._workers[worker_id] = Worker(position, compensation)
        return True

    def register(self, worker_id: str, timestamp: int) -> bool:
        worker = self._workers.get(worker_id)
        if worker is None:
            return False
        if worker.entered_at is None:
            worker.entered_at = timestamp
        else:
            worker.total += timestamp - worker.entered_at
            worker.entered_at = None
        return True

    def get_total_time(self, worker_id: str) -> int | None:
        worker = self._workers.get(worker_id)
        return None if worker is None else worker.total

    def top_n_workers(self, n: int, position: str) -> list[str]:
        ranked = sorted(((worker_id, worker) for worker_id, worker
                         in self._workers.items() if worker.position == position),
                        key=lambda item: (-item[1].total, item[0]))
        return [f"{worker_id}({worker.total})"
                for worker_id, worker in ranked[:max(n, 0)]]
