"""Reference solution — all four levels.

Two choices carry the whole thing:

* **The id's number is the creation order.** Keeping it on the task as an int
  makes the level-2 tie-break a plain sort key; comparing the id *strings*
  would put "task_id_10" before "task_id_9".
* **Assignments are records that are never deleted.** Each has a start, a
  finish and a completed flag. "Active", "overdue" and the quota count are all
  predicates evaluated at the timestamp of the call, so expiry needs no
  clean-up, and level 4 is one flag plus the other half of the same predicate.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Task:
    """One task. `number` is when it was created, and its id is derived from it."""

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
    completed: bool = False

    def active_at(self, timestamp: int) -> bool:
        return not self.completed and self.start <= timestamp < self.finish

    def overdue_at(self, timestamp: int) -> bool:
        return not self.completed and self.finish <= timestamp


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._issued = 0
        self._quotas: dict[str, int] = {}
        self._assignments: dict[str, list[Assignment]] = {}

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def _ranked(tasks: list[Task], limit: int) -> list[str]:
        if limit <= 0:
            return []
        ordered = sorted(tasks, key=lambda task: task.rank)
        return [task.task_id for task in ordered[:limit]]

    @staticmethod
    def _by_deadline(assignments: list[Assignment]) -> list[str]:
        ordered = sorted(assignments, key=lambda a: (a.finish, a.start))
        return [assignment.task_id for assignment in ordered]

    # --- Level 1 -----------------------------------------------------------

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

    # --- Level 2 -----------------------------------------------------------

    def search_tasks(self, timestamp: int, name_filter: str,
                     max_results: int) -> list[str]:
        matches = [task for task in self._tasks.values()
                   if name_filter in task.name]
        return self._ranked(matches, max_results)

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        return self._ranked(list(self._tasks.values()), limit)

    # --- Level 3 -----------------------------------------------------------

    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self._quotas:
            return False
        self._quotas[user_id] = quota
        self._assignments[user_id] = []
        return True

    def assign_task(self, timestamp: int, task_id: str, user_id: str,
                    finish_time: int) -> bool:
        if task_id not in self._tasks or user_id not in self._quotas:
            return False
        mine = self._assignments[user_id]
        active = sum(1 for a in mine if a.active_at(timestamp))
        if active >= self._quotas[user_id]:
            return False
        mine.append(Assignment(task_id, timestamp, finish_time))
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        return self._by_deadline([a for a in self._assignments.get(user_id, [])
                                  if a.active_at(timestamp)])

    # --- Level 4 -----------------------------------------------------------

    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        matches = [a for a in self._assignments.get(user_id, [])
                   if a.task_id == task_id and a.active_at(timestamp)]
        if not matches:
            return False
        # The oldest live assignment of that task is the one that is finished.
        min(matches, key=lambda a: a.start).completed = True
        return True

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        return self._by_deadline([a for a in self._assignments.get(user_id, [])
                                  if a.overdue_at(timestamp)])
