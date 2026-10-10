"""Checkpoint: the reference solution after level 1 only."""

from dataclasses import dataclass


@dataclass(slots=True)
class Task:
    name: str
    priority: int


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._issued = 0

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self._issued += 1
        task_id = f"task_id_{self._issued}"
        self._tasks[task_id] = Task(name, priority)
        return task_id

    def update_task(self, timestamp: int, task_id: str, name: str,
                    priority: int) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.name = name
        task.priority = priority
        return True

    def get_task(self, timestamp: int, task_id: str) -> str | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        return f'{{"name":"{task.name}","priority":{task.priority}}}'
