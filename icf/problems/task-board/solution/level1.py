"""Checkpoint: the reference solution after level 1 only."""

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


class TaskBoard:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskState] = {}     # live tasks only

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
        return self._tasks.pop(task_id, None) is not None
