"""Level 2 — search and ranking (visible cases)."""
from icf_testkit import case, expect


@case("list_tasks_sorted puts the highest priority first")
def list_by_priority(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "Low", 1)
    tm.add_task(2, "High", 5)
    tm.add_task(3, "Mid", 3)
    expect(tm.list_tasks_sorted(4, 10), ["task_id_2", "task_id_3", "task_id_1"])


@case("tasks with the same priority stay in creation order")
def ties_keep_creation_order(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 2)
    tm.add_task(2, "b", 7)
    tm.add_task(3, "c", 2)
    tm.add_task(4, "d", 2)
    expect(tm.list_tasks_sorted(5, 10),
           ["task_id_2", "task_id_1", "task_id_3", "task_id_4"])


@case("the limit caps the list, and a limit of zero or less gives []")
def limit_caps_the_list(TaskManager):
    tm = TaskManager()
    for ts, priority in ((1, 1), (2, 2), (3, 3)):
        tm.add_task(ts, f"t{priority}", priority)
    expect(tm.list_tasks_sorted(4, 2), ["task_id_3", "task_id_2"])
    expect(tm.list_tasks_sorted(5, 0), [])
    expect(tm.list_tasks_sorted(6, -1), [])


@case("search_tasks matches part of the name and ranks the matches")
def search_matches_substring(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "Write report", 2)
    tm.add_task(2, "Read report", 4)
    tm.add_task(3, "Call supplier", 9)
    expect(tm.search_tasks(4, "report", 10), ["task_id_2", "task_id_1"])


@case("a search that matches nothing returns an empty list")
def search_no_match(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "Write report", 2)
    expect(tm.search_tasks(2, "report", 5), ["task_id_1"])
    expect(tm.search_tasks(3, "invoice", 5), [])
