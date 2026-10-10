"""Level 3 — users and quotas (visible cases)."""
from icf_testkit import case, expect


@case("a user holds the tasks assigned to them, listed like list_tasks")
def assign_and_list(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "docs", "Write docs", 2)
    board.create_task(2, "bug", "Fix bug", 5)
    expect(board.add_user(3, "ana", 5), True)
    expect(board.assign_task(4, "docs", "ana"), True)
    expect(board.assign_task(5, "bug", "ana"), True)
    expect(board.get_user_tasks(6, "ana"), ["bug(5)", "docs(2)"])


@case("a user cannot hold more tasks than the quota allows")
def quota_enforced(TaskBoard):
    board = TaskBoard()
    for ts, task_id in enumerate(("a", "b", "c"), start=1):
        board.create_task(ts, task_id, task_id.upper(), 1)
    board.add_user(4, "ana", 2)
    expect(board.assign_task(5, "a", "ana"), True)
    expect(board.assign_task(6, "b", "ana"), True)
    expect(board.assign_task(7, "c", "ana"), False, "the quota is 2")
    expect(board.get_user_tasks(8, "ana"), ["a(1)", "b(1)"])


@case("a user id can only be registered once, and the quota stays as it was")
def add_user_once(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 1)
    expect(board.add_user(3, "ana", 1), True)
    expect(board.add_user(4, "ana", 5), False)
    expect(board.assign_task(5, "a", "ana"), True)
    expect(board.assign_task(6, "b", "ana"), False, "the quota is still 1")


@case("assigning a task to another user moves it, freeing the first user's slot")
def reassign_moves(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "bug", "Fix bug", 5)
    board.create_task(2, "docs", "Write docs", 2)
    board.add_user(3, "ana", 1)
    board.add_user(4, "ben", 1)
    board.assign_task(5, "bug", "ana")
    expect(board.assign_task(6, "bug", "ben"), True)
    expect(board.get_user_tasks(7, "ana"), [])
    expect(board.get_user_tasks(8, "ben"), ["bug(5)"])
    expect(board.assign_task(9, "docs", "ana"), True, "ana's slot is free again")


@case("unassign takes a task back, and is refused if nobody holds it")
def unassign(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "bug", "Fix bug", 5)
    board.add_user(2, "ana", 1)
    board.assign_task(3, "bug", "ana")
    expect(board.unassign_task(4, "bug"), True)
    expect(board.get_user_tasks(5, "ana"), [])
    expect(board.unassign_task(6, "bug"), False, "not assigned any more")
    expect(board.unassign_task(7, "ghost"), False, "no such task")


@case("assigning is refused for a missing task or user, or a task the user already holds")
def assign_refusals(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "bug", "Fix bug", 5)
    board.add_user(2, "ana", 3)
    expect(board.assign_task(3, "ghost", "ana"), False, "no such task")
    expect(board.assign_task(4, "bug", "nobody"), False, "no such user")
    expect(board.assign_task(5, "bug", "ana"), True)
    expect(board.assign_task(6, "bug", "ana"), False, "ana already holds it")
    expect(board.get_user_tasks(7, "ana"), ["bug(5)"])


@case("an unknown user has no task list at all; a user holding nothing has an empty one")
def user_tasks_unknown(TaskBoard):
    board = TaskBoard()
    board.add_user(1, "ana", 2)
    expect(board.get_user_tasks(2, "ana"), [])
    expect(board.get_user_tasks(3, "ghost"), None)
