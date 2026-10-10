"""Level 4 — completion and overdue work (hidden cases)."""
import random

from icf_testkit import case, expect


@case("with a task assigned twice, the assignment that started earliest is completed")
def earliest_start_is_completed(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 3)
    tm.assign_task(3, "task_id_1", "ana", 100)   # starts first, finishes last
    tm.assign_task(4, "task_id_1", "ana", 50)
    expect(tm.complete_task(5, "task_id_1", "ana"), True)
    expect(tm.get_user_tasks(6, "ana"), ["task_id_1"])
    expect(tm.get_overdue_assignments(60, "ana"), ["task_id_1"],
           "the one finishing at 50 was not the one completed")
    expect(tm.get_overdue_assignments(101, "ana"), ["task_id_1"],
           "the one that started at 3 was completed, so it never becomes overdue")


@case("overdue assignments sort by finish time, then start, and repeat a task")
def overdue_order(TaskManager):
    tm = TaskManager()
    for ts in (1, 2, 3):
        tm.add_task(ts, f"t{ts}", 1)
    tm.add_user(4, "ana", 5)
    tm.assign_task(5, "task_id_2", "ana", 30)
    tm.assign_task(6, "task_id_1", "ana", 20)
    tm.assign_task(7, "task_id_1", "ana", 30)
    tm.assign_task(8, "task_id_3", "ana", 25)
    expect(tm.get_overdue_assignments(40, "ana"),
           ["task_id_1", "task_id_3", "task_id_2", "task_id_1"])


@case("an expired assignment can no longer be completed")
def expired_cannot_be_completed(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.assign_task(3, "task_id_1", "ana", 5)
    expect(tm.complete_task(5, "task_id_1", "ana"), False, "it expired at exactly 5")
    expect(tm.get_overdue_assignments(6, "ana"), ["task_id_1"], "and it stays overdue")


@case("completing an assignment affects only that user")
def completion_is_per_user(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.add_user(3, "ben", 1)
    tm.assign_task(4, "task_id_1", "ana", 20)
    tm.assign_task(5, "task_id_1", "ben", 20)
    expect(tm.complete_task(6, "task_id_1", "ana"), True)
    expect(tm.get_user_tasks(7, "ben"), ["task_id_1"])
    expect(tm.get_overdue_assignments(21, "ben"), ["task_id_1"])
    expect(tm.get_overdue_assignments(22, "ana"), [])


@case("get_overdue_assignments for an unknown user is an empty list")
def overdue_unknown_user(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.assign_task(3, "task_id_1", "ana", 4)
    expect(tm.get_overdue_assignments(5, "ana"), ["task_id_1"])
    expect(tm.get_overdue_assignments(6, "ghost"), [])


@case("a user cannot complete a task that is assigned only to someone else")
def complete_someone_elses_task(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.add_user(3, "ben", 1)
    tm.assign_task(4, "task_id_1", "ana", 50)
    expect(tm.complete_task(5, "task_id_1", "ben"), False)
    expect(tm.get_user_tasks(6, "ana"), ["task_id_1"], "ana's assignment is untouched")


@case("a completed slot can be reused, and the new assignment can become overdue")
def reuse_after_completion(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    tm.add_user(2, "ana", 1)
    tm.assign_task(3, "task_id_1", "ana", 100)
    tm.complete_task(4, "task_id_1", "ana")
    expect(tm.assign_task(5, "task_id_1", "ana", 10), True)
    expect(tm.get_overdue_assignments(10, "ana"), ["task_id_1"])
    expect(tm.get_overdue_assignments(101, "ana"), ["task_id_1"],
           "the completed one never joins the list")


@case("completion, quotas and overdue reports match a reference model")
def fuzz_against_model(TaskManager):
    rng = random.Random(5150)
    tm = TaskManager()
    task_count = 0
    quotas = {}
    assignments = {}   # user -> [[task_id, start, finish, completed]]
    users = ["ana", "ben", "cy"]

    def active(user, ts):
        return [a for a in assignments.get(user, []) if not a[3] and a[1] <= ts < a[2]]

    def by_deadline(items):
        return [a[0] for a in sorted(items, key=lambda a: (a[2], a[1]))]

    for ts in range(1, 800):
        roll = rng.random()
        if roll < 0.08:
            tm.add_task(ts, "t", 1)
            task_count += 1
        elif roll < 0.15:
            user = rng.choice(users)
            quota = rng.randrange(1, 4)
            expect(tm.add_user(ts, user, quota), user not in quotas, f"add_user at ts={ts}")
            if user not in quotas:
                quotas[user] = quota
                assignments[user] = []
        elif roll < 0.5:
            user = rng.choice(users)
            number = rng.randrange(1, task_count + 2)
            finish = ts + rng.randrange(1, 30)
            ok = (user in quotas and number <= task_count
                  and len(active(user, ts)) < quotas[user])
            expect(tm.assign_task(ts, f"task_id_{number}", user, finish), ok,
                   f"assign_task at ts={ts}")
            if ok:
                assignments[user].append([f"task_id_{number}", ts, finish, False])
        elif roll < 0.7:
            user = rng.choice(users + ["ghost"])
            task_id = f"task_id_{rng.randrange(1, task_count + 2)}"
            matches = [a for a in active(user, ts) if a[0] == task_id]
            expect(tm.complete_task(ts, task_id, user), bool(matches),
                   f"complete_task({task_id}, {user}) at ts={ts}")
            if matches:
                min(matches, key=lambda a: a[1])[3] = True
        elif roll < 0.85:
            user = rng.choice(users + ["ghost"])
            expect(tm.get_user_tasks(ts, user), by_deadline(active(user, ts)),
                   f"get_user_tasks({user}) at ts={ts}")
        else:
            user = rng.choice(users + ["ghost"])
            overdue = [a for a in assignments.get(user, []) if not a[3] and a[2] <= ts]
            expect(tm.get_overdue_assignments(ts, user), by_deadline(overdue),
                   f"get_overdue_assignments({user}) at ts={ts}")
