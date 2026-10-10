"""Level 1 — tasks (hidden cases)."""
import random

from icf_testkit import case, expect


def as_dict(title, priority, created_at):
    return {"title": title, "priority": priority, "created_at": created_at}


@case("several tasks may share a title, and priorities may be zero or negative")
def shared_titles_and_odd_priorities(TaskBoard):
    board = TaskBoard()
    expect(board.create_task(1, "a", "Same", 0), True)
    expect(board.create_task(2, "b", "Same", -4), True)
    expect(board.get_task(3, "a"), as_dict("Same", 0, 1))
    expect(board.get_task(4, "b"), as_dict("Same", -4, 2))


@case("task ids are compared exactly, so 't1' and 'T1' are different tasks")
def ids_are_case_sensitive(TaskBoard):
    board = TaskBoard()
    expect(board.create_task(1, "t1", "lower", 1), True)
    expect(board.create_task(2, "T1", "upper", 2), True)
    expect(board.get_task(3, "T1"), as_dict("upper", 2, 2))
    expect(board.delete_task(4, "T1"), True)
    expect(board.get_task(5, "t1"), as_dict("lower", 1, 1))


@case("updating or deleting one task leaves the others alone")
def tasks_are_independent(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 2)
    board.create_task(3, "c", "C", 3)
    board.update_task(4, "a", "A2", 10)
    board.delete_task(5, "b")
    expect(board.get_task(6, "a"), as_dict("A2", 10, 1))
    expect(board.get_task(7, "b"), None)
    expect(board.get_task(8, "c"), as_dict("C", 3, 3))


@case("an update that changes nothing still succeeds")
def no_op_update(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    expect(board.update_task(2, "a", "A", 1), True)
    expect(board.get_task(3, "a"), as_dict("A", 1, 1))


@case("changing a returned dictionary does not change the task")
def returned_dict_is_a_copy(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    got = board.get_task(2, "a")
    got["title"] = "sabotage"
    got["priority"] = 99
    expect(board.get_task(3, "a"), as_dict("A", 1, 1))


@case("a refused create does not overwrite the task that holds the id")
def refused_create_is_inert(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.update_task(2, "a", "A2", 2)
    expect(board.create_task(3, "a", "Z", 9), False)
    expect(board.get_task(4, "a"), as_dict("A2", 2, 1))


@case("an id can be deleted and created again many times, each a new task")
def repeated_reuse(TaskBoard):
    board = TaskBoard()
    for round_ in range(5):
        start = 10 * round_ + 1
        expect(board.create_task(start, "t", f"round {round_}", round_), True,
               f"round {round_}")
        expect(board.get_task(start + 1, "t"),
               as_dict(f"round {round_}", round_, start))
        expect(board.delete_task(start + 2, "t"), True)
    expect(board.get_task(100, "t"), None)


@case("a random workload of creates, updates and deletes matches a reference model")
def fuzz_against_model(TaskBoard):
    rng = random.Random(4242)
    board = TaskBoard()
    live = {}
    ids = ["t1", "t2", "t3", "t4", "t5"]
    for ts in range(1, 600):
        task_id = rng.choice(ids)
        title = rng.choice(["Plan", "Build", "Ship"])
        priority = rng.randrange(-3, 6)
        roll = rng.random()
        if roll < 0.3:
            ok = task_id not in live
            expect(board.create_task(ts, task_id, title, priority), ok,
                   f"create_task({task_id}) at ts={ts}")
            if ok:
                live[task_id] = as_dict(title, priority, ts)
        elif roll < 0.55:
            ok = task_id in live
            expect(board.update_task(ts, task_id, title, priority), ok,
                   f"update_task({task_id}) at ts={ts}")
            if ok:
                live[task_id] = as_dict(title, priority, live[task_id]["created_at"])
        elif roll < 0.7:
            ok = task_id in live
            expect(board.delete_task(ts, task_id), ok,
                   f"delete_task({task_id}) at ts={ts}")
            live.pop(task_id, None)
        else:
            expect(board.get_task(ts, task_id), live.get(task_id),
                   f"get_task({task_id}) at ts={ts}")
