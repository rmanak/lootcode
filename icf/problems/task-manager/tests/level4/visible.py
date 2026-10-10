"""Level 4 — completion and overdue work (visible cases)."""
from icf_testkit import case, expect


@case("complete_task finishes the assignment and removes it from the user's tasks")
def complete_removes_assignment(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 2)
    tm.assign_task(3, "task_id_1", "ana", 100)
    expect(tm.complete_task(4, "task_id_1", "ana"), True)
    expect(tm.get_user_tasks(5, "ana"), [])


@case("completing an assignment frees its quota slot immediately")
def complete_frees_slot(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_task(2, "b", 1)
    tm.add_user(3, "ana", 1)
    tm.assign_task(4, "task_id_1", "ana", 100)
    expect(tm.assign_task(5, "task_id_2", "ana", 100), False, "the slot is taken")
    expect(tm.complete_task(6, "task_id_1", "ana"), True)
    expect(tm.assign_task(7, "task_id_2", "ana", 100), True, "the slot was freed")


@case("complete_task is refused when there is no active assignment to complete")
def complete_refused(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_task(2, "b", 1)
    tm.add_user(3, "ana", 5)
    tm.assign_task(4, "task_id_1", "ana", 100)
    expect(tm.complete_task(5, "task_id_1", "ghost"), False, "unknown user")
    expect(tm.complete_task(6, "task_id_9", "ana"), False, "unknown task")
    expect(tm.complete_task(7, "task_id_2", "ana"), False, "task_id_2 was never assigned")
    expect(tm.complete_task(8, "task_id_1", "ana"), True)
    expect(tm.complete_task(9, "task_id_1", "ana"), False, "already completed")


@case("an assignment that reaches its finish time without completion is overdue")
def becomes_overdue(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.assign_task(3, "task_id_1", "ana", 10)
    expect(tm.get_overdue_assignments(9, "ana"), [], "not yet at its finish time")
    expect(tm.get_overdue_assignments(10, "ana"), ["task_id_1"])


@case("completed assignments are never overdue")
def completed_not_overdue(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_task(2, "b", 1)
    tm.add_user(3, "ana", 2)
    tm.assign_task(4, "task_id_1", "ana", 10)
    tm.assign_task(5, "task_id_2", "ana", 10)
    expect(tm.complete_task(6, "task_id_1", "ana"), True)
    expect(tm.get_overdue_assignments(11, "ana"), ["task_id_2"])
