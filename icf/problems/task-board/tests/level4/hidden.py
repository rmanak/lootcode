"""Level 4 — history (hidden cases)."""
import random
from bisect import bisect_right

from icf_testkit import case, expect


def as_dict(title, priority, created_at):
    return {"title": title, "priority": priority, "created_at": created_at}


@case("a reused id keeps one history: the new task's changes follow the old one's")
def history_across_reuse(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "Old", 1)
    board.delete_task(2, "a")
    board.create_task(3, "a", "New", 2)
    board.update_task(4, "a", "Newer", 2)
    expect(board.get_task_history(5, "a"),
           ["1:created", "2:deleted", "3:created", "4:updated"])


@case("a move between users is one assigned entry, naming the new holder")
def reassign_is_one_entry(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.add_user(2, "ana", 1)
    board.add_user(3, "ben", 1)
    board.assign_task(4, "a", "ana")
    board.assign_task(5, "a", "ben")
    board.unassign_task(6, "a")
    expect(board.get_task_history(7, "a"),
           ["1:created", "4:assigned:ana", "5:assigned:ben", "6:unassigned:ben"])


@case("deleting an assigned task records only the deletion")
def delete_assigned_is_one_entry(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.add_user(2, "ana", 1)
    board.assign_task(3, "a", "ana")
    board.delete_task(4, "a")
    expect(board.get_task_history(5, "a"), ["1:created", "3:assigned:ana", "4:deleted"])


@case("an update that changes nothing is still recorded")
def noop_update_recorded(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.update_task(2, "a", "A", 1)
    expect(board.get_task_history(3, "a"), ["1:created", "2:updated"])


@case("each task's history holds only its own changes")
def history_is_per_task(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 1)
    board.add_user(3, "ana", 1)
    board.assign_task(4, "b", "ana")
    board.assign_task(5, "a", "ana")          # refused: the quota is full
    board.assign_task(6, "b", "ana")          # refused: ana already holds it
    board.update_task(7, "ghost", "G", 1)     # refused: no such task
    board.delete_task(8, "a")
    board.delete_task(9, "a")                 # refused: already deleted
    board.create_task(10, "ghost", "G", 0)
    expect(board.get_task_history(11, "a"), ["1:created", "8:deleted"])
    expect(board.get_task_history(12, "b"), ["2:created", "4:assigned:ana"])
    expect(board.get_task_history(13, "ghost"), ["10:created"])


@case("changing the returned history does not change the stored one")
def history_is_a_copy(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    got = board.get_task_history(2, "a")
    got.append("99:deleted")
    got[0] = "sabotage"
    expect(board.get_task_history(3, "a"), ["1:created"])


@case("get_task_at follows a reused id through each of its tasks, with a gap between")
def task_at_across_reuse(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "Old", 1)
    board.update_task(2, "a", "Old v2", 3)
    board.delete_task(4, "a")
    board.create_task(8, "a", "New", 5)
    expect(board.get_task_at(9, "a", 3), as_dict("Old v2", 3, 1))
    expect(board.get_task_at(10, "a", 6), None,
           "between the deletion and the re-creation")
    expect(board.get_task_at(11, "a", 8), as_dict("New", 5, 8))
    expect(board.get_task_at(12, "a", 0), None)
    expect(board.get_task_at(13, "never", 12), None)


@case("changing a dictionary from get_task_at does not change the past")
def task_at_is_a_copy(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.update_task(2, "a", "B", 2)
    got = board.get_task_at(3, "a", 1)
    got["title"] = "sabotage"
    expect(board.get_task_at(4, "a", 1), as_dict("A", 1, 1))


@case("list_tasks_at sorts each id by the created_at of the task that held it then")
def list_at_reuse_order(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 2)
    board.create_task(2, "b", "B", 2)
    board.delete_task(3, "a")
    board.create_task(4, "a", "A again", 2)
    expect(board.list_tasks_at(5, 2, 10), ["a(2)", "b(2)"], "the first 'a' was created at 1")
    expect(board.list_tasks_at(6, 3, 10), ["b(2)"])
    expect(board.list_tasks_at(7, 4, 10), ["b(2)", "a(2)"], "the second 'a' was created at 4")


@case("list_tasks_at respects the limit, and lists nothing before the first task")
def list_at_limits(TaskBoard):
    board = TaskBoard()
    board.create_task(5, "a", "A", 1)
    board.create_task(6, "b", "B", 3)
    board.create_task(7, "c", "C", 2)
    expect(board.list_tasks_at(8, 7, 2), ["b(3)", "c(2)"])
    expect(board.list_tasks_at(9, 8, 0), [])
    expect(board.list_tasks_at(10, 4, 10), [])
    expect(board.list_tasks_at(11, 11, 10), ["b(3)", "c(2)", "a(1)"], "at the present moment")


@case("looking at the past changes nothing in the present")
def past_queries_are_read_only(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.update_task(2, "a", "A2", 4)
    board.get_task_at(3, "a", 1)
    board.list_tasks_at(4, 1, 10)
    board.get_task_history(5, "a")
    expect(board.get_task(6, "a"), as_dict("A2", 4, 1))
    expect(board.list_tasks(7, 10), ["a(4)"])
    expect(board.get_task_history(8, "a"), ["1:created", "2:updated"])


@case("history and past states match a reference model over a random workload")
def fuzz_against_model(TaskBoard):
    rng = random.Random(20260913)
    board = TaskBoard()
    quotas = {"ana": 1, "ben": 2}
    board.add_user(1, "ana", 1)
    board.add_user(2, "ben", 2)
    ids = ["a", "b", "c", "d"]
    live = {}                 # task id -> (title, priority, created_at)
    holder = {}               # live task id -> user id
    history = {}              # task id -> entries
    moments = [0]             # timestamps of the snapshots below
    snapshots = [{}]          # a copy of `live` after each call

    def state_at(time_at):
        return snapshots[bisect_right(moments, time_at) - 1]

    for ts in range(10, 800):
        task_id = rng.choice(ids)
        roll = rng.random()
        if roll < 0.2:
            title, priority = rng.choice(["x", "y"]), rng.randrange(-2, 4)
            ok = task_id not in live
            expect(board.create_task(ts, task_id, title, priority), ok,
                   f"create_task({task_id}) at ts={ts}")
            if ok:
                live[task_id] = (title, priority, ts)
                history.setdefault(task_id, []).append(f"{ts}:created")
        elif roll < 0.35:
            title, priority = rng.choice(["x", "y"]), rng.randrange(-2, 4)
            ok = task_id in live
            expect(board.update_task(ts, task_id, title, priority), ok,
                   f"update_task({task_id}) at ts={ts}")
            if ok:
                live[task_id] = (title, priority, live[task_id][2])
                history[task_id].append(f"{ts}:updated")
        elif roll < 0.45:
            ok = task_id in live
            expect(board.delete_task(ts, task_id), ok,
                   f"delete_task({task_id}) at ts={ts}")
            if ok:
                del live[task_id]
                holder.pop(task_id, None)
                history[task_id].append(f"{ts}:deleted")
        elif roll < 0.6:
            user = rng.choice(list(quotas))
            ok = (task_id in live and holder.get(task_id) != user
                  and sum(1 for u in holder.values() if u == user) < quotas[user])
            expect(board.assign_task(ts, task_id, user), ok,
                   f"assign_task({task_id}, {user}) at ts={ts}")
            if ok:
                holder[task_id] = user
                history[task_id].append(f"{ts}:assigned:{user}")
        elif roll < 0.68:
            ok = task_id in holder
            expect(board.unassign_task(ts, task_id), ok,
                   f"unassign_task({task_id}) at ts={ts}")
            if ok:
                history[task_id].append(f"{ts}:unassigned:{holder.pop(task_id)}")
        elif roll < 0.78:
            expect(board.get_task_history(ts, task_id), history.get(task_id),
                   f"get_task_history({task_id}) at ts={ts}")
        elif roll < 0.9:
            time_at = rng.randrange(0, ts + 1)
            state = state_at(time_at).get(task_id)
            expect(board.get_task_at(ts, task_id, time_at),
                   as_dict(*state) if state else None,
                   f"get_task_at({task_id}, {time_at}) at ts={ts}")
        else:
            time_at = rng.randrange(0, ts + 1)
            limit = rng.randrange(0, 6)
            then = sorted(state_at(time_at).items(),
                          key=lambda kv: (-kv[1][1], kv[1][2]))
            expect(board.list_tasks_at(ts, time_at, limit),
                   [f"{t}({s[1]})" for t, s in then][:limit],
                   f"list_tasks_at({time_at}, {limit}) at ts={ts}")
        moments.append(ts)
        snapshots.append(dict(live))
