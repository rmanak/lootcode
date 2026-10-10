"""Checkpoint: the reference solution after levels 1-3 (no history yet)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskState:
    """What a task looks like. Frozen: a change is a new state."""

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


class TaskBoard:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskState] = {}   # live tasks only
        self._quotas: dict[str, int] = {}
        self._holder: dict[str, str] = {}        # task id -> user id
        self._held: dict[str, set[str]] = {}     # user id -> task ids

    def _ranked(self, task_ids, limit: int) -> list[str]:
        if limit <= 0:
            return []
        ordered = sorted(task_ids, key=lambda task_id: self._tasks[task_id].rank)
        return [f"{task_id}({self._tasks[task_id].priority})"
                for task_id in ordered[:limit]]

    def _release(self, task_id: str) -> str | None:
        user_id = self._holder.pop(task_id, None)
        if user_id is not None:
            self._held[user_id].discard(task_id)
        return user_id

    def create_task(self, timestamp: int, task_id: str, title: str,
                    priority: int) -> bool:
        if task_id in self._tasks:
            return False
        self._tasks[task_id] = TaskState(title, priority, timestamp)
        return True

    def get_task(self, timestamp: int, task_id: str) -> dict | None:
        task = self._tasks.get(task_id)
        return None if task is None else task.as_dict()

    def update_task(self, timestamp: int, task_id: str, title: str,
                    priority: int) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        # A task keeps the creation time it has always had.
        self._tasks[task_id] = TaskState(title, priority, task.created_at)
        return True

    def delete_task(self, timestamp: int, task_id: str) -> bool:
        if task_id not in self._tasks:
            return False
        self._release(task_id)
        del self._tasks[task_id]
        return True

    def list_tasks(self, timestamp: int, limit: int) -> list[str]:
        return self._ranked(list(self._tasks), limit)

    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self._quotas:
            return False
        self._quotas[user_id] = quota
        self._held[user_id] = set()
        return True

    def assign_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        if task_id not in self._tasks or user_id not in self._quotas:
            return False
        if self._holder.get(task_id) == user_id:
            return False
        if len(self._held[user_id]) >= self._quotas[user_id]:
            return False
        self._release(task_id)
        self._holder[task_id] = user_id
        self._held[user_id].add(task_id)
        return True

    def unassign_task(self, timestamp: int, task_id: str) -> bool:
        return self._release(task_id) is not None

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str] | None:
        if user_id not in self._quotas:
            return None
        held = self._held[user_id]
        return self._ranked(list(held), len(held))
