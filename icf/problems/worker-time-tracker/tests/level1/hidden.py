"""Level 1 — office attendance (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a refused add_worker leaves the existing worker's time untouched")
def refused_add_keeps_worker(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    wt.register("ana", 1)
    wt.register("ana", 5)
    expect(wt.add_worker("ana", "Developer", 10), False)
    expect(wt.get_total_time("ana"), 4)


@case("workers' sessions are independent, even when they overlap")
def overlapping_workers(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    wt.add_worker("ben", "Developer", 10)
    wt.register("ana", 1)
    wt.register("ben", 2)
    wt.register("ana", 10)
    wt.register("ben", 20)
    expect(wt.get_total_time("ana"), 9)
    expect(wt.get_total_time("ben"), 18)


@case("a refused register does not disturb anyone's session")
def refused_register_is_inert(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    wt.register("ana", 1)
    expect(wt.register("ghost", 2), False)
    expect(wt.register("ana", 5), True, "this is still ana's exit")
    expect(wt.get_total_time("ana"), 4)


@case("many short sessions add up exactly")
def many_sessions(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    for i in range(50):
        wt.register("ana", 10 * i + 1)
        wt.register("ana", 10 * i + 8)
    expect(wt.get_total_time("ana"), 350)


@case("worker ids are case-sensitive")
def ids_case_sensitive(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    expect(wt.add_worker("ana", "Developer", 10), True)
    expect(wt.add_worker("Ana", "Developer", 10), True, "a different worker")
    wt.register("ana", 1)
    wt.register("ana", 3)
    expect(wt.get_total_time("ana"), 2)
    expect(wt.get_total_time("Ana"), 0)


@case("a worker added after others have been in the office starts at zero")
def late_worker(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    wt.register("ana", 100)
    wt.register("ana", 200)
    wt.add_worker("ben", "Developer", 10)
    expect(wt.get_total_time("ben"), 0)
    wt.register("ben", 300)
    wt.register("ben", 301)
    expect(wt.get_total_time("ben"), 1)
    expect(wt.get_total_time("ana"), 100)


@case("time in the office matches a reference model over a random workload")
def fuzz_against_model(WorkerTimeTracker):
    rng = random.Random(2024)
    wt = WorkerTimeTracker()
    totals, entered = {}, {}
    names = ["ana", "ben", "cy", "dee", "ghost"]
    timestamp = 0
    for step in range(800):
        roll = rng.random()
        who = rng.choice(names)
        if roll < 0.1:
            ok = who not in totals
            expect(wt.add_worker(who, "Developer", 10), ok, f"add_worker({who}) at step {step}")
            if ok:
                totals[who] = 0
        elif roll < 0.7:
            timestamp += rng.randrange(1, 20)
            ok = who in totals
            expect(wt.register(who, timestamp), ok, f"register({who}, {timestamp})")
            if ok:
                if who in entered:
                    totals[who] += timestamp - entered.pop(who)
                else:
                    entered[who] = timestamp
        else:
            expect(wt.get_total_time(who), totals.get(who),
                   f"get_total_time({who}) at step {step}")
