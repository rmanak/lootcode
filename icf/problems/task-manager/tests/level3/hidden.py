"""Level 3 — users, quotas and deadlines (hidden cases)."""
import random

from icf_testkit import case, expect


@case("the same task can be assigned to the same user twice, taking two slots")
def same_task_twice(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_task(2, "b", 1)
    tm.add_user(3, "ana", 2)
    expect(tm.assign_task(4, "task_id_1", "ana", 40), True)
    expect(tm.assign_task(5, "task_id_1", "ana", 30), True)
    expect(tm.assign_task(6, "task_id_2", "ana", 50), False, "both slots are taken")
    expect(tm.get_user_tasks(7, "ana"), ["task_id_1", "task_id_1"])


@case("a user with a quota of 0 can never be assigned anything")
def zero_quota(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "idle", 0)
    tm.add_user(3, "busy", 1)
    expect(tm.assign_task(4, "task_id_1", "idle", 10), False)
    expect(tm.assign_task(5, "task_id_1", "busy", 10), True)
    expect(tm.get_user_tasks(6, "idle"), [])


@case("a refused add_user keeps the original quota")
def refused_add_user_keeps_quota(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    expect(tm.add_user(2, "ana", 1), True)
    expect(tm.add_user(3, "ana", 5), False)
    expect(tm.assign_task(4, "task_id_1", "ana", 100), True)
    expect(tm.assign_task(5, "task_id_1", "ana", 100), False, "the quota is still 1")


@case("get_user_tasks for an unknown user is an empty list")
def unknown_user_tasks(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.assign_task(3, "task_id_1", "ana", 10)
    expect(tm.get_user_tasks(4, "ana"), ["task_id_1"])
    expect(tm.get_user_tasks(5, "ghost"), [])


@case("one task can be assigned to several users, each against their own quota")
def task_shared_by_users(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_task(2, "b", 1)
    tm.add_user(3, "ana", 1)
    tm.add_user(4, "ben", 1)
    expect(tm.assign_task(5, "task_id_1", "ana", 20), True)
    expect(tm.assign_task(6, "task_id_1", "ben", 25), True,
           "ben's quota is separate from ana's")
    expect(tm.assign_task(7, "task_id_2", "ben", 25), False, "ben's slot is taken")
    expect(tm.get_user_tasks(8, "ana"), ["task_id_1"])
    expect(tm.get_user_tasks(9, "ben"), ["task_id_1"])


@case("updating a task does not change its assignments")
def update_keeps_assignments(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.assign_task(3, "task_id_1", "ana", 30)
    expect(tm.update_task(4, "task_id_1", "renamed", 9), True)
    expect(tm.get_user_tasks(5, "ana"), ["task_id_1"])


@case("an assignment that ends one tick after it starts is active for that one tick")
def one_tick_assignment(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    expect(tm.assign_task(5, "task_id_1", "ana", 6), True)
    expect(tm.get_user_tasks(6, "ana"), [], "active only during [5, 6)")
    expect(tm.assign_task(7, "task_id_1", "ana", 9), True, "the slot is free again")


@case("the quota counts only the assignments active at the moment of the call")
def quota_counts_active_only(TaskManager):
    tm = TaskManager()
    for ts in range(1, 6):
        tm.add_task(ts, f"t{ts}", 1)
    tm.add_user(6, "ana", 2)
    expect(tm.assign_task(7, "task_id_1", "ana", 9), True)
    expect(tm.assign_task(8, "task_id_2", "ana", 100), True)
    expect(tm.assign_task(9, "task_id_3", "ana", 100), True, "task_id_1 expired at 9")
    expect(tm.assign_task(10, "task_id_4", "ana", 100), False)
    expect(tm.get_user_tasks(11, "ana"), ["task_id_2", "task_id_3"])


@case("assignments and quotas match a reference model over a random workload")
def fuzz_against_model(TaskManager):
    rng = random.Random(9001)
    tm = TaskManager()
    task_count = 0
    quotas = {}
    assignments = {}   # user -> [(task_id, start, finish)]
    users = ["ana", "ben", "cy", "dee"]

    def active(user, ts):
        return [a for a in assignments.get(user, []) if a[1] <= ts < a[2]]

    for ts in range(1, 700):
        roll = rng.random()
        if roll < 0.1:
            tm.add_task(ts, "t", 1)
            task_count += 1
        elif roll < 0.2:
            user = rng.choice(users)
            quota = rng.randrange(0, 4)
            expect(tm.add_user(ts, user, quota), user not in quotas,
                   f"add_user({user}) at ts={ts}")
            if user not in quotas:
                quotas[user] = quota
                assignments[user] = []
        elif roll < 0.65:
            user = rng.choice(users + ["ghost"])
            task_id = f"task_id_{rng.randrange(1, task_count + 3)}"
            finish = ts + rng.randrange(1, 40)
            ok = (user in quotas and int(task_id.rsplit("_", 1)[1]) <= task_count
                  and len(active(user, ts)) < quotas[user])
            expect(tm.assign_task(ts, task_id, user, finish), ok,
                   f"assign_task({task_id}, {user}, {finish}) at ts={ts}")
            if ok:
                assignments[user].append((task_id, ts, finish))
        else:
            user = rng.choice(users + ["ghost"])
            want = [a[0] for a in sorted(active(user, ts), key=lambda a: (a[2], a[1]))]
            expect(tm.get_user_tasks(ts, user), want, f"get_user_tasks({user}) at ts={ts}")
