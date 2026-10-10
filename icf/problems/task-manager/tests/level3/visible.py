"""Level 3 — users, quotas and deadlines (visible cases)."""
from icf_testkit import case, expect


@case("a user can be registered only once")
def add_user_once(TaskManager):
    tm = TaskManager()
    expect(tm.add_user(1, "ana", 2), True)
    expect(tm.add_user(2, "ana", 5), False, "the id is taken")


@case("an assignment is active from its start until just before its finish")
def assignment_window(TaskManager):
    tm = TaskManager()
    task_id = tm.add_task(1, "Write report", 2)
    tm.add_user(2, "ana", 2)
    expect(tm.assign_task(10, task_id, "ana", 20), True)
    expect(tm.get_user_tasks(11, "ana"), [task_id])
    expect(tm.get_user_tasks(19, "ana"), [task_id], "still before the finish time")
    expect(tm.get_user_tasks(20, "ana"), [], "expired at exactly the finish time")


@case("assign_task is refused for an unknown task or user")
def assign_unknown(TaskManager):
    tm = TaskManager()
    task_id = tm.add_task(1, "Write report", 2)
    tm.add_user(2, "ana", 5)
    expect(tm.assign_task(3, "task_id_9", "ana", 50), False, "no such task")
    expect(tm.assign_task(4, task_id, "ben", 50), False, "no such user")
    expect(tm.assign_task(5, task_id, "ana", 50), True)
    expect(tm.get_user_tasks(6, "ana"), [task_id], "only the valid assignment exists")


@case("a user cannot hold more active assignments than the quota")
def quota_is_enforced(TaskManager):
    tm = TaskManager()
    for ts in (1, 2, 3):
        tm.add_task(ts, f"t{ts}", 1)
    tm.add_user(4, "ana", 2)
    expect(tm.assign_task(5, "task_id_1", "ana", 100), True)
    expect(tm.assign_task(6, "task_id_2", "ana", 100), True)
    expect(tm.assign_task(7, "task_id_3", "ana", 100), False, "the quota is 2")
    expect(tm.get_user_tasks(8, "ana"), ["task_id_1", "task_id_2"])


@case("an expired assignment frees its quota slot by itself")
def expiry_frees_the_slot(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_task(2, "b", 1)
    tm.add_user(3, "ana", 1)
    expect(tm.assign_task(4, "task_id_1", "ana", 10), True)
    expect(tm.assign_task(6, "task_id_2", "ana", 30), False, "the slot is taken until 10")
    expect(tm.assign_task(10, "task_id_2", "ana", 30), True, "the slot was freed at 10")
    expect(tm.get_user_tasks(11, "ana"), ["task_id_2"])


@case("get_user_tasks sorts by finish time, then by when the assignment was made")
def user_tasks_order(TaskManager):
    tm = TaskManager()
    for ts in (1, 2, 3):
        tm.add_task(ts, f"t{ts}", 1)
    tm.add_user(4, "ana", 5)
    tm.assign_task(5, "task_id_1", "ana", 50)
    tm.assign_task(6, "task_id_2", "ana", 30)
    tm.assign_task(7, "task_id_3", "ana", 50)
    expect(tm.get_user_tasks(8, "ana"), ["task_id_2", "task_id_1", "task_id_3"])
