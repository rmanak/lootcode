"""Level 4 — history (visible cases)."""
from icf_testkit import case, expect


@case("the history lists every change to a task, oldest first")
def basic_history(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "bug", "Fix bug", 3)
    board.add_user(2, "ana", 1)
    board.assign_task(3, "bug", "ana")
    board.update_task(4, "bug", "Fix bug now", 9)
    board.unassign_task(5, "bug")
    board.delete_task(6, "bug")
    expect(board.get_task_history(7, "bug"),
           ["1:created", "3:assigned:ana", "4:updated", "5:unassigned:ana",
            "6:deleted"])


@case("the history survives deletion, and an id that was never used has none")
def history_after_delete(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.delete_task(2, "a")
    expect(board.get_task_history(3, "a"), ["1:created", "2:deleted"])
    expect(board.get_task_history(4, "ghost"), None)


@case("operations that are refused are not recorded")
def refusals_not_recorded(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "a", "dup", 1)       # the id is taken
    board.add_user(3, "ana", 0)
    board.assign_task(4, "a", "ana")          # the quota is 0
    board.unassign_task(5, "a")               # nobody holds it
    expect(board.get_task_history(6, "a"), ["1:created"])


@case("get_task_at shows a task as it was, including a change at exactly that moment")
def task_at(TaskBoard):
    board = TaskBoard()
    board.create_task(10, "a", "Draft", 1)
    board.update_task(20, "a", "Final", 5)
    expect(board.get_task_at(30, "a", 9), None, "not created yet")
    expect(board.get_task_at(31, "a", 10),
           {"title": "Draft", "priority": 1, "created_at": 10})
    expect(board.get_task_at(32, "a", 19),
           {"title": "Draft", "priority": 1, "created_at": 10})
    expect(board.get_task_at(33, "a", 20),
           {"title": "Final", "priority": 5, "created_at": 10})


@case("get_task_at is None from the moment a task was deleted")
def task_at_after_delete(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.delete_task(5, "a")
    expect(board.get_task_at(6, "a", 4),
           {"title": "A", "priority": 1, "created_at": 1})
    expect(board.get_task_at(7, "a", 5), None)


@case("list_tasks_at lists the tasks that existed then, with the priorities they had")
def list_at(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 2)
    board.update_task(3, "a", "A", 7)
    board.delete_task(4, "b")
    board.create_task(5, "c", "C", 4)
    expect(board.list_tasks_at(6, 2, 10), ["b(2)", "a(1)"])
    expect(board.list_tasks_at(7, 3, 10), ["a(7)", "b(2)"])
    expect(board.list_tasks_at(8, 4, 10), ["a(7)"])
    expect(board.list_tasks_at(9, 9, 10), ["a(7)", "c(4)"])
