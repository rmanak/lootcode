"""Level 2 — priority order (hidden cases)."""
import random

from icf_testkit import case, expect


@case("an updated task keeps its place in time among tasks of its new priority")
def update_keeps_creation_place(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "first", "F", 1)
    board.create_task(2, "second", "S", 5)
    board.create_task(3, "third", "T", 5)
    board.update_task(4, "first", "F", 5)
    expect(board.list_tasks(5, 10), ["first(5)", "second(5)", "third(5)"],
           "first was created before the other two")
    board.update_task(6, "second", "S renamed", 5)
    expect(board.list_tasks(7, 10), ["first(5)", "second(5)", "third(5)"],
           "an update is not a re-creation")


@case("a re-created id sorts as a new task, after older tasks of its priority")
def recreated_goes_to_the_back(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 4)
    board.create_task(2, "b", "B", 4)
    board.delete_task(3, "a")
    board.create_task(4, "a", "A again", 4)
    expect(board.list_tasks(5, 10), ["b(4)", "a(4)"])


@case("creation order is by time, not by id: 't10' created before 't9' comes first")
def numeric_looking_ids(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "t10", "x", 0)
    board.create_task(2, "t9", "x", 0)
    board.create_task(3, "t1", "x", 0)
    expect(board.list_tasks(4, 3), ["t10(0)", "t9(0)", "t1(0)"])


@case("negative priorities sort below zero")
def negative_priorities(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "neg", "N", -3)
    board.create_task(2, "zero", "Z", 0)
    board.create_task(3, "minus1", "M", -1)
    expect(board.list_tasks(4, 10), ["zero(0)", "minus1(-1)", "neg(-3)"])


@case("a limit equal to the number of tasks returns them all, and 1 returns the top")
def limit_boundaries(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 2)
    board.create_task(2, "b", "B", 2)
    expect(board.list_tasks(3, 2), ["a(2)", "b(2)"])
    expect(board.list_tasks(4, 1), ["a(2)"])


@case("a deleted task that was the most important no longer leads the list")
def deleted_leader(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "boss", "B", 100)
    board.create_task(2, "a", "A", 1)
    expect(board.list_tasks(3, 1), ["boss(100)"])
    board.delete_task(4, "boss")
    expect(board.list_tasks(5, 1), ["a(1)"])


@case("the ordering matches a reference model over a random workload")
def fuzz_ordering(TaskBoard):
    rng = random.Random(1234)
    board = TaskBoard()
    live = {}   # task id -> (priority, created_at)
    ids = [f"t{n}" for n in range(1, 13)]
    for ts in range(1, 700):
        task_id = rng.choice(ids)
        priority = rng.randrange(-2, 5)
        roll = rng.random()
        if roll < 0.35:
            if board.create_task(ts, task_id, "t", priority):
                live[task_id] = (priority, ts)
        elif roll < 0.55:
            if board.update_task(ts, task_id, "u", priority):
                live[task_id] = (priority, live[task_id][1])
        elif roll < 0.7:
            board.delete_task(ts, task_id)
            live.pop(task_id, None)
        else:
            limit = rng.randrange(0, 14)
            ordered = sorted(live.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
            wanted = [f"{t}({p})" for t, (p, _) in ordered][:limit]
            expect(board.list_tasks(ts, limit), wanted,
                   f"list_tasks({limit}) at ts={ts}")
