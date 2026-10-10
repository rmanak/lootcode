"""Checkpoint: the reference solution after levels 1 to 3 (nothing is completed yet)."""

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


@dataclass(slots=True)
class Assignment:
    """One task handed to one user, due over the window [start, finish)."""

    task_id: str
    start: int
    finish: int

    def active_at(self, timestamp: int) -> bool:
        return self.start <= timestamp < self.finish


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._issued = 0
        self._quotas: dict[str, int] = {}
        self._assignments: dict[str, list[Assignment]] = {}

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

    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self._quotas:
            return False
        self._quotas[user_id] = quota
        self._assignments[user_id] = []
        return True

    def _active(self, user_id: str, timestamp: int) -> list[Assignment]:
        return [a for a in self._assignments.get(user_id, [])
                if a.active_at(timestamp)]

    def assign_task(self, timestamp: int, task_id: str, user_id: str,
                    finish_time: int) -> bool:
        if task_id not in self._tasks or user_id not in self._quotas:
            return False
        if len(self._active(user_id, timestamp)) >= self._quotas[user_id]:
            return False
        self._assignments[user_id].append(
            Assignment(task_id, timestamp, finish_time))
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        active = sorted(self._active(user_id, timestamp),
                        key=lambda a: (a.finish, a.start))
        return [assignment.task_id for assignment in active]
