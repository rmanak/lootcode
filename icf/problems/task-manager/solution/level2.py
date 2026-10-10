"""Checkpoint: the reference solution after levels 1 and 2."""

from dataclasses import dataclass


@dataclass(slots=True)
class Task:
    """`number` is the creation order — the level-2 tie-break."""

    number: int
    name: str
    priority: int

    @property
    def task_id(self) -> str:
        return f"task_id_{self.number}"

    @property
    def rank(self) -> tuple[int, int]:
        """Sort key: highest priority first, and older first on a tie."""
        return (-self.priority, self.number)


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._issued = 0

    @staticmethod
    def _ranked(tasks: list[Task], limit: int) -> list[str]:
        if limit <= 0:
            return []
        ordered = sorted(tasks, key=lambda task: task.rank)
        return [task.task_id for task in ordered[:limit]]

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self._issued += 1
        task = Task(self._issued, name, priority)
        self._tasks[task.task_id] = task
        return task.task_id

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

    def search_tasks(self, timestamp: int, name_filter: str,
                     max_results: int) -> list[str]:
        matches = [task for task in self._tasks.values()
                   if name_filter in task.name]
        return self._ranked(matches, max_results)

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        return self._ranked(list(self._tasks.values()), limit)
