"""Level 1 — tasks (visible cases)."""
from icf_testkit import case, expect


@case("add_task hands out ids in creation order")
def ids_in_creation_order(TaskManager):
    tm = TaskManager()
    expect(tm.add_task(1, "Write report", 3), "task_id_1")
    expect(tm.add_task(2, "Email team", 1), "task_id_2")
    expect(tm.add_task(3, "Plan sprint", 5), "task_id_3")


@case("get_task returns the task as compact JSON, name first")
def get_task_as_json(TaskManager):
    tm = TaskManager()
    task_id = tm.add_task(1, "Write report", 3)
    expect(tm.get_task(2, task_id), '{"name":"Write report","priority":3}')


@case("get_task returns None for an id that was never issued")
def get_task_missing(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "Write report", 3)
    expect(tm.get_task(2, "task_id_1"), '{"name":"Write report","priority":3}')
    expect(tm.get_task(3, "task_id_2"), None, "only one task was added")
    expect(tm.get_task(4, "task_id_0"), None, "ids start at 1")


@case("update_task replaces the name and the priority")
def update_replaces_both(TaskManager):
    tm = TaskManager()
    task_id = tm.add_task(1, "Write report", 3)
    expect(tm.update_task(2, task_id, "Write final report", 8), True)
    expect(tm.get_task(3, task_id), '{"name":"Write final report","priority":8}')


@case("update_task on an unknown id returns False and creates nothing")
def update_unknown_id(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "Write report", 3)
    expect(tm.update_task(2, "task_id_2", "Ghost", 1), False)
    expect(tm.get_task(3, "task_id_2"), None, "the update did not create a task")
    expect(tm.get_task(4, "task_id_1"), '{"name":"Write report","priority":3}')


@case("several tasks may share a name, each with its own id")
def shared_names(TaskManager):
    tm = TaskManager()
    first = tm.add_task(1, "Standup", 2)
    second = tm.add_task(2, "Standup", 2)
    expect([first, second], ["task_id_1", "task_id_2"])
    expect(tm.update_task(3, second, "Standup", 9), True)
    expect(tm.get_task(4, first), '{"name":"Standup","priority":2}',
           "the other task is untouched")
    expect(tm.get_task(5, second), '{"name":"Standup","priority":9}')
