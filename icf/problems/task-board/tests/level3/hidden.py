"""Level 3 — users and quotas (hidden cases)."""
import random

from icf_testkit import case, expect


@case("deleting a task releases it, freeing the holder's slot immediately")
def delete_releases(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 1)
    board.add_user(3, "ana", 1)
    board.assign_task(4, "a", "ana")
    expect(board.delete_task(5, "a"), True)
    expect(board.get_user_tasks(6, "ana"), [])
    expect(board.assign_task(7, "b", "ana"), True)


@case("a task created with a reused id is not assigned to anyone")
def recreated_is_unassigned(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.add_user(2, "ana", 2)
    board.assign_task(3, "a", "ana")
    board.delete_task(4, "a")
    board.create_task(5, "a", "A again", 1)
    expect(board.get_user_tasks(6, "ana"), [])
    expect(board.unassign_task(7, "a"), False, "the new task has no holder")
    expect(board.assign_task(8, "a", "ana"), True)


@case("a move to a user with no room is refused, and the task stays where it was")
def refused_move_keeps_holder(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 2)
    board.add_user(3, "ana", 1)
    board.add_user(4, "ben", 1)
    board.assign_task(5, "a", "ana")
    board.assign_task(6, "b", "ben")
    expect(board.assign_task(7, "a", "ben"), False)
    expect(board.get_user_tasks(8, "ana"), ["a(1)"])
    expect(board.get_user_tasks(9, "ben"), ["b(2)"])


@case("a user with a quota of 0 can never hold a task")
def zero_quota(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.add_user(2, "idle", 0)
    board.add_user(3, "busy", 1)
    expect(board.assign_task(4, "a", "idle"), False)
    expect(board.assign_task(5, "a", "busy"), True)
    expect(board.get_user_tasks(6, "idle"), [])


@case("updating a task keeps its holder, and the holder's list follows the new priority")
def update_keeps_holder(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 5)
    board.add_user(3, "ana", 2)
    board.assign_task(4, "a", "ana")
    board.assign_task(5, "b", "ana")
    expect(board.get_user_tasks(6, "ana"), ["b(5)", "a(1)"])
    board.update_task(7, "a", "A urgent", 8)
    expect(board.get_user_tasks(8, "ana"), ["a(8)", "b(5)"])


@case("a deleted task can be neither assigned nor unassigned")
def deleted_task_cannot_be_assigned(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.add_user(2, "ana", 1)
    board.assign_task(3, "a", "ana")
    board.delete_task(4, "a")
    expect(board.unassign_task(5, "a"), False)
    expect(board.assign_task(6, "a", "ana"), False)
    expect(board.get_user_tasks(7, "ana"), [])


@case("users and tasks have separate ids: a user may share a name with a task")
def separate_namespaces(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "x", "X", 1)
    expect(board.add_user(2, "x", 1), True)
    expect(board.assign_task(3, "x", "x"), True)
    expect(board.get_user_tasks(4, "x"), ["x(1)"])


@case("ties in a user's list are broken by creation time, not by assignment time")
def user_list_ties(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "z", "Z", 3)
    board.create_task(2, "a", "A", 3)
    board.add_user(3, "ana", 2)
    board.assign_task(4, "a", "ana")
    board.assign_task(5, "z", "ana")
    expect(board.get_user_tasks(6, "ana"), ["z(3)", "a(3)"],
           "z was created first, even though it was assigned second")


@case("a slot freed by unassigning can be used straight away")
def unassign_frees_slot(TaskBoard):
    board = TaskBoard()
    board.create_task(1, "a", "A", 1)
    board.create_task(2, "b", "B", 1)
    board.add_user(3, "ana", 1)
    board.assign_task(4, "a", "ana")
    expect(board.assign_task(5, "b", "ana"), False)
    board.unassign_task(6, "a")
    expect(board.assign_task(7, "b", "ana"), True)
    expect(board.get_user_tasks(8, "ana"), ["b(1)"])


@case("assignments and quotas match a reference model over a random workload")
def fuzz_against_model(TaskBoard):
    rng = random.Random(8675309)
    board = TaskBoard()
    ids = ["a", "b", "c", "d", "e", "f"]
    users = ["ana", "ben", "cy"]
    live = {}      # task id -> (priority, created_at)
    holder = {}    # live task id -> user id
    quotas = {}

    def holding(user):
        return sum(1 for held_by in holder.values() if held_by == user)

    for ts in range(1, 800):
        task_id = rng.choice(ids)
        user = rng.choice(users + ["ghost"])
        roll = rng.random()
        if roll < 0.15:
            priority = rng.randrange(0, 4)
            ok = task_id not in live
            expect(board.create_task(ts, task_id, "t", priority), ok,
                   f"create_task({task_id}) at ts={ts}")
            if ok:
                live[task_id] = (priority, ts)
        elif roll < 0.22:
            priority = rng.randrange(0, 4)
            ok = task_id in live
            expect(board.update_task(ts, task_id, "u", priority), ok,
                   f"update_task({task_id}) at ts={ts}")
            if ok:
                live[task_id] = (priority, live[task_id][1])
        elif roll < 0.3:
            ok = task_id in live
            expect(board.delete_task(ts, task_id), ok,
                   f"delete_task({task_id}) at ts={ts}")
            live.pop(task_id, None)
            holder.pop(task_id, None)
        elif roll < 0.36:
            new_user = rng.choice(users)
            ok = new_user not in quotas
            quota = rng.randrange(0, 4)
            expect(board.add_user(ts, new_user, quota), ok,
                   f"add_user({new_user}) at ts={ts}")
            if ok:
                quotas[new_user] = quota
        elif roll < 0.6:
            ok = (task_id in live and user in quotas
                  and holder.get(task_id) != user
                  and holding(user) < quotas[user])
            expect(board.assign_task(ts, task_id, user), ok,
                   f"assign_task({task_id}, {user}) at ts={ts}")
            if ok:
                holder[task_id] = user
        elif roll < 0.7:
            ok = task_id in holder
            expect(board.unassign_task(ts, task_id), ok,
                   f"unassign_task({task_id}) at ts={ts}")
            holder.pop(task_id, None)
        else:
            if user not in quotas:
                wanted = None
            else:
                mine = [t for t, held_by in holder.items() if held_by == user]
                mine.sort(key=lambda t: (-live[t][0], live[t][1]))
                wanted = [f"{t}({live[t][0]})" for t in mine]
            expect(board.get_user_tasks(ts, user), wanted,
                   f"get_user_tasks({user}) at ts={ts}")
