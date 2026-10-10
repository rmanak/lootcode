"""Level 2 — search and ranking (hidden cases)."""
import random

from icf_testkit import case, expect


@case("creation order is numeric, so task_id_10 comes after task_id_9")
def creation_order_is_numeric(TaskManager):
    tm = TaskManager()
    for ts in range(1, 12):
        tm.add_task(ts, "same", 0)
    expect(tm.list_tasks_sorted(20, 20), [f"task_id_{n}" for n in range(1, 12)])
    expect(tm.search_tasks(21, "same", 3), ["task_id_1", "task_id_2", "task_id_3"])


@case("search is case-sensitive")
def search_is_case_sensitive(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "Report", 1)
    tm.add_task(2, "report card", 1)
    expect(tm.search_tasks(3, "report", 10), ["task_id_2"])
    expect(tm.search_tasks(4, "Report", 10), ["task_id_1"])


@case("the empty filter matches every task")
def empty_filter_matches_all(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_task(2, "b", 3)
    tm.add_task(3, "c", 2)
    expect(tm.search_tasks(4, "", 10), ["task_id_2", "task_id_3", "task_id_1"])


@case("max_results caps the search, and zero or less gives []")
def max_results_caps(TaskManager):
    tm = TaskManager()
    for ts in range(1, 6):
        tm.add_task(ts, "job", ts)
    expect(tm.search_tasks(10, "job", 2), ["task_id_5", "task_id_4"])
    expect(tm.search_tasks(11, "job", 0), [])
    expect(tm.search_tasks(12, "job", -3), [])


@case("an update re-ranks the task but never changes its creation order")
def update_re_ranks(TaskManager):
    tm = TaskManager()
    for ts in (1, 2, 3):
        tm.add_task(ts, "t", 1)
    tm.update_task(4, "task_id_3", "t", 9)
    expect(tm.list_tasks_sorted(5, 10), ["task_id_3", "task_id_1", "task_id_2"])
    tm.update_task(6, "task_id_3", "t", 1)
    expect(tm.list_tasks_sorted(7, 10), ["task_id_1", "task_id_2", "task_id_3"],
           "back to priority 1, it returns to its creation position")


@case("search sees a renamed task by its new name only")
def search_after_rename(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "old name", 1)
    tm.add_task(2, "other", 1)
    tm.update_task(3, "task_id_1", "new name", 1)
    expect(tm.search_tasks(4, "new", 5), ["task_id_1"])
    expect(tm.search_tasks(5, "old", 5), [])


@case("negative priorities sort below zero")
def negative_priorities(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", -2)
    tm.add_task(2, "b", 0)
    tm.add_task(3, "c", -10)
    expect(tm.list_tasks_sorted(4, 5), ["task_id_2", "task_id_1", "task_id_3"])


@case("an empty task manager lists and searches as empty")
def empty_manager(TaskManager):
    tm = TaskManager()
    expect(tm.list_tasks_sorted(1, 5), [])
    expect(tm.search_tasks(2, "", 5), [])
    tm.add_task(3, "x", 1)
    expect(tm.list_tasks_sorted(4, 5), ["task_id_1"])


@case("rankings and searches match a reference model over a random workload")
def fuzz_against_model(TaskManager):
    rng = random.Random(777)
    tm = TaskManager()
    model = []  # index = creation number - 1, value = [name, priority]
    names = ["write report", "read report", "Report", "call", "port"]

    def ranked(indexes, limit):
        if limit <= 0:
            return []
        ordered = sorted(indexes, key=lambda i: (-model[i][1], i))
        return [f"task_id_{i + 1}" for i in ordered[:limit]]

    for ts in range(1, 500):
        roll = rng.random()
        if roll < 0.3 or not model:
            name, priority = rng.choice(names), rng.randrange(-2, 6)
            tm.add_task(ts, name, priority)
            model.append([name, priority])
        elif roll < 0.5:
            index = rng.randrange(len(model))
            name, priority = rng.choice(names), rng.randrange(-2, 6)
            tm.update_task(ts, f"task_id_{index + 1}", name, priority)
            model[index] = [name, priority]
        elif roll < 0.75:
            limit = rng.randrange(-1, 15)
            expect(tm.list_tasks_sorted(ts, limit), ranked(range(len(model)), limit),
                   f"list_tasks_sorted(limit={limit}) at ts={ts}")
        else:
            needle = rng.choice(["report", "port", "Re", "", "call", "zzz"])
            limit = rng.randrange(-1, 10)
            matches = [i for i in range(len(model)) if needle in model[i][0]]
            expect(tm.search_tasks(ts, needle, limit), ranked(matches, limit),
                   f"search_tasks({needle!r}, {limit}) at ts={ts}")
