"""Checkpoint: the reference solution after levels 1 to 3 (no double pay yet)."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Promotion:
    """A new position and rate, waiting for the worker's next entry."""

    position: str
    compensation: int


@dataclass(frozen=True, slots=True)
class Session:
    """One completed stretch on the clock, [enter, leave), paid at `rate`."""

    enter: int
    leave: int
    rate: int


@dataclass(slots=True)
class Worker:
    position: str
    compensation: int
    pending: Promotion | None = None
    entered_at: int | None = None            # None when off the clock
    sessions: list[Session] = field(default_factory=list)
    total: int = 0

    def enter(self, timestamp: int) -> None:
        """Start a session — the moment a pending promotion takes effect."""
        if self.pending is not None:
            self.position = self.pending.position
            self.compensation = self.pending.compensation
            self.pending = None
        self.entered_at = timestamp

    def leave(self, timestamp: int) -> None:
        """Close the open session at the rate it was opened with."""
        self.sessions.append(
            Session(self.entered_at, timestamp, self.compensation))
        self.total += timestamp - self.entered_at
        self.entered_at = None


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
            worker.enter(timestamp)
        else:
            worker.leave(timestamp)
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

    def promote(self, worker_id: str, new_position: str,
                new_compensation: int) -> bool:
        worker = self._workers.get(worker_id)
        if worker is None or worker.pending is not None:
            return False
        worker.pending = Promotion(new_position, new_compensation)
        return True

    def calc_salary(self, worker_id: str, start_timestamp: int,
                    end_timestamp: int) -> int | None:
        worker = self._workers.get(worker_id)
        if worker is None:
            return None
        return sum(session.rate * max(0, min(session.leave, end_timestamp)
                                      - max(session.enter, start_timestamp))
                   for session in worker.sessions)
