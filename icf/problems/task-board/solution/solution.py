"""Reference solution — all four levels.

Two choices carry the whole thing:

* **A task's place in line is its creation time, not its id.** Ids are chosen
  by the caller and come back after a delete, so neither the id string nor the
  order a dict happens to hold them in is the tie-break; ``created_at`` is, and
  it is part of the task from level 1.
* **Nothing is overwritten.** Every id owns a timeline of snapshots, where the
  state is ``None`` from a deletion on. The current task is the last snapshot,
  a delete is one more snapshot, and "as of ``time_at``" is a binary search
  over the same list — so level 4 is a lookup rather than a replay of
  everything that happened.
"""

from bisect import bisect_right
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskState:
    """What a task looked like at one moment. Frozen: a change is a new state."""

    title: str
    priority: int
    created_at: int

    def as_dict(self) -> dict:
        return {"title": self.title, "priority": self.priority,
                "created_at": self.created_at}

    @property
    def rank(self) -> tuple[int, int]:
        """Sort key: highest priority first, and older first on a tie."""
        return (-self.priority, self.created_at)


@dataclass(frozen=True, slots=True)
class Snapshot:
    """A task's state from `at` onwards; a state of None means it was deleted."""

    at: int
    state: TaskState | None


class TaskBoard:
    def __init__(self) -> None:
        self._timelines: dict[str, list[Snapshot]] = {}
        self._history: dict[str, list[str]] = {}
        self._quotas: dict[str, int] = {}
        self._holder: dict[str, str] = {}        # live task id -> user id
        self._held: dict[str, set[str]] = {}     # user id -> live task ids

    # --- helpers -----------------------------------------------------------

    def _current(self, task_id: str) -> TaskState | None:
        timeline = self._timelines.get(task_id)
        return timeline[-1].state if timeline else None

    def _state_at(self, task_id: str, time_at: int) -> TaskState | None:
        timeline = self._timelines[task_id]
        index = bisect_right([snapshot.at for snapshot in timeline], time_at)
        return timeline[index - 1].state if index else None

    def _record(self, timestamp: int, task_id: str, state: TaskState | None,
                event: str) -> None:
        self._timelines.setdefault(task_id, []).append(Snapshot(timestamp, state))
        self._log(timestamp, task_id, event)

    def _log(self, timestamp: int, task_id: str, event: str) -> None:
        self._history.setdefault(task_id, []).append(f"{timestamp}:{event}")

    @staticmethod
    def _ranked(tasks: list[tuple[str, TaskState]], limit: int) -> list[str]:
        if limit <= 0:
            return []
        ordered = sorted(tasks, key=lambda item: item[1].rank)
        return [f"{task_id}({state.priority})" for task_id, state in ordered[:limit]]

    def _release(self, task_id: str) -> str | None:
        user_id = self._holder.pop(task_id, None)
        if user_id is not None:
            self._held[user_id].discard(task_id)
        return user_id

    # --- Level 1 -----------------------------------------------------------

    def create_task(self, timestamp: int, task_id: str, title: str,
                    priority: int) -> bool:
        if self._current(task_id) is not None:
            return False
        self._record(timestamp, task_id,
                     TaskState(title, priority, timestamp), "created")
        return True

    def get_task(self, timestamp: int, task_id: str) -> dict | None:
        state = self._current(task_id)
        return None if state is None else state.as_dict()

    def update_task(self, timestamp: int, task_id: str, title: str,
                    priority: int) -> bool:
        state = self._current(task_id)
        if state is None:
            return False
        # A task keeps the creation time it has always had.
        self._record(timestamp, task_id,
                     TaskState(title, priority, state.created_at), "updated")
        return True

    def delete_task(self, timestamp: int, task_id: str) -> bool:
        if self._current(task_id) is None:
            return False
        self._release(task_id)
        self._record(timestamp, task_id, None, "deleted")
        return True

    # --- Level 2 -----------------------------------------------------------

    def list_tasks(self, timestamp: int, limit: int) -> list[str]:
        live = [(task_id, timeline[-1].state)
                for task_id, timeline in self._timelines.items()
                if timeline[-1].state is not None]
        return self._ranked(live, limit)

    # --- Level 3 -----------------------------------------------------------

    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self._quotas:
            return False
        self._quotas[user_id] = quota
        self._held[user_id] = set()
        return True

    def assign_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        if self._current(task_id) is None or user_id not in self._quotas:
            return False
        if self._holder.get(task_id) == user_id:
            return False
        if len(self._held[user_id]) >= self._quotas[user_id]:
            return False
        self._release(task_id)
        self._holder[task_id] = user_id
        self._held[user_id].add(task_id)
        self._log(timestamp, task_id, f"assigned:{user_id}")
        return True

    def unassign_task(self, timestamp: int, task_id: str) -> bool:
        user_id = self._release(task_id)
        if user_id is None:
            return False
        self._log(timestamp, task_id, f"unassigned:{user_id}")
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str] | None:
        if user_id not in self._quotas:
            return None
        held = self._held[user_id]
        return self._ranked([(task_id, self._current(task_id)) for task_id in held],
                            len(held))

    # --- Level 4 -----------------------------------------------------------

    def get_task_history(self, timestamp: int, task_id: str) -> list[str] | None:
        history = self._history.get(task_id)
        return list(history) if history is not None else None

    def get_task_at(self, timestamp: int, task_id: str,
                    time_at: int) -> dict | None:
        if task_id not in self._timelines:
            return None
        state = self._state_at(task_id, time_at)
        return None if state is None else state.as_dict()

    def list_tasks_at(self, timestamp: int, time_at: int,
                      limit: int) -> list[str]:
        then = [(task_id, state) for task_id in self._timelines
                if (state := self._state_at(task_id, time_at)) is not None]
        return self._ranked(then, limit)
