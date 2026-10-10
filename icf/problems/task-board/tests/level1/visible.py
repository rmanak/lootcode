"""Level 1 — tasks (visible cases)."""
from icf_testkit import case, expect


@case("a created task can be read back")
def create_then_get(TaskBoard):
    board = TaskBoard()
    expect(board.create_task(1, "t1", "Write report", 3), True)
    expect(board.get_task(2, "t1"),
           {"title": "Write report", "priority": 3, "created_at": 1})


@case("a task id can only be in use once")
def duplicate_id_refused(TaskBoard):
    board = TaskBoard()
    expect(board.create_task(1, "t1", "Write report", 3), True)
    expect(board.create_task(2, "t1", "Something else", 9), False, "the id is taken")
    expect(board.get_task(3, "t1"),
           {"title": "Write report", "priority": 3, "created_at": 1},
           "the original task is untouched")


@case("reading a task that does not exist returns None")
def get_missing(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "t1", "Write report", 3)
    expect(board.get_task(2, "t1"),
           {"title": "Write report", "priority": 3, "created_at": 1},
           "the task that does exist")
    expect(board.get_task(3, "t2"), None)


@case("update replaces the title and priority, but created_at stays")
def update_keeps_created_at(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "t1", "Write report", 3)
    expect(board.update_task(5, "t1", "Write the final report", 8), True)
    expect(board.get_task(6, "t1"),
           {"title": "Write the final report", "priority": 8, "created_at": 1})


@case("updating a task that does not exist is refused and creates nothing")
def update_missing(TaskBoard):
    board = TaskBoard()
    expect(board.update_task(1, "t1", "Ghost", 1), False)
    expect(board.get_task(2, "t1"), None, "no task was created")
    expect(board.create_task(3, "t1", "Real", 2), True, "the id is still free")


@case("delete removes the task, and a second delete is refused")
def delete_task(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "t1", "Write report", 3)
    expect(board.delete_task(2, "t1"), True)
    expect(board.get_task(3, "t1"), None)
    expect(board.delete_task(4, "t1"), False, "already deleted")
    expect(board.update_task(5, "t1", "Back?", 1), False,
           "a deleted task cannot be updated")


@case("a deleted id can be used again, and the new task has its own created_at")
def reuse_after_delete(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "t1", "Old", 3)
    board.delete_task(2, "t1")
    expect(board.create_task(7, "t1", "New", 5), True)
    expect(board.get_task(8, "t1"), {"title": "New", "priority": 5, "created_at": 7})
