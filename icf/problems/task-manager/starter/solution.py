class TaskManager:
    """A team's task list.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: tasks ---------------------------------------------------

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        pass

    def update_task(self, timestamp: int, task_id: str, name: str,
                    priority: int) -> bool:
        pass

    def get_task(self, timestamp: int, task_id: str) -> str | None:
        pass

    # --- Level 2: search and ranking --------------------------------------

    def search_tasks(self, timestamp: int, name_filter: str,
                     max_results: int) -> list[str]:
        pass

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        pass

    # --- Level 3: users, quotas and deadlines -----------------------------

    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        pass

    def assign_task(self, timestamp: int, task_id: str, user_id: str,
                    finish_time: int) -> bool:
        pass

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        pass

    # --- Level 4: completion and overdue work -----------------------------

    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        pass

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        pass
