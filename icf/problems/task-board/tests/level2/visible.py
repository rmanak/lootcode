"""Level 2 — priority order (visible cases)."""
from icf_testkit import case, expect


@case("tasks are listed from the highest priority to the lowest")
def by_priority(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "low", "Low", 1)
    board.create_task(2, "high", "High", 9)
    board.create_task(3, "mid", "Mid", 4)
    expect(board.list_tasks(4, 10), ["high(9)", "mid(4)", "low(1)"])


@case("tasks with the same priority are listed in the order they were created")
def ties_by_creation(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "zulu", "Z", 5)
    board.create_task(2, "alpha", "A", 5)
    board.create_task(3, "mike", "M", 5)
    expect(board.list_tasks(4, 10), ["zulu(5)", "alpha(5)", "mike(5)"])


@case("limit caps the list, and a larger limit returns every task")
def limit_caps(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 2)
    board.create_task(3, "c", "C", 3)
    expect(board.list_tasks(4, 2), ["c(3)", "b(2)"])
    expect(board.list_tasks(5, 99), ["c(3)", "b(2)", "a(1)"])


@case("an empty board, or a limit of 0, lists nothing")
def degenerate(TaskBoard):
    board = TaskBoard()
    expect(board.list_tasks(1, 5), [])
    board.create_task(2, "a", "A", 1)
    expect(board.list_tasks(3, 0), [])
    expect(board.list_tasks(4, 1), ["a(1)"])


@case("an updated priority moves the task, and deleted tasks are not listed")
def update_and_delete_reflected(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 2)
    board.create_task(3, "c", "C", 3)
    board.update_task(4, "a", "A", 7)
    board.delete_task(5, "c")
    expect(board.list_tasks(6, 10), ["a(7)", "b(2)"])
