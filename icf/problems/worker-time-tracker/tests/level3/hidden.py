"""Level 3 — promotions and salary (hidden cases)."""
import random

from icf_testkit import case, expect


def session(wt, worker_id, enter, leave):
    wt.register(worker_id, enter)
    wt.register(worker_id, leave)


@case("a second promotion is refused while the first is still pending")
def second_promotion_refused(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    expect(wt.promote("ana", "Senior", 20), True)
    expect(wt.promote("ana", "Lead", 30), False)
    session(wt, "ana", 1, 11)
    expect(wt.top_n_workers(5, "Senior"), ["ana(10)"], "the first promotion won")
    expect(wt.top_n_workers(5, "Lead"), [])
    expect(wt.calc_salary("ana", 0, 100), 200)


@case("once a promotion has taken effect, the worker can be promoted again")
def promote_again(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    expect(wt.promote("ana", "A", 20), True)
    wt.register("ana", 1)                       # A takes effect
    expect(wt.promote("ana", "B", 30), True, "the pending slot is free again")
    wt.register("ana", 11)                      # [1, 11) at 20
    session(wt, "ana", 20, 30)                  # B takes effect: [20, 30) at 30
    expect(wt.calc_salary("ana", 0, 100), 500)
    expect(wt.top_n_workers(5, "B"), ["ana(20)"])


@case("the salary period is half-open: its end is not included")
def half_open_period(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 1)
    session(wt, "ana", 10, 20)
    expect(wt.calc_salary("ana", 10, 20), 10)
    expect(wt.calc_salary("ana", 20, 30), 0)
    expect(wt.calc_salary("ana", 19, 20), 1)
    expect(wt.calc_salary("ana", 0, 10), 0)
    expect(wt.calc_salary("ana", 0, 11), 1)


@case("an open session earns nothing until the worker leaves")
def open_session_unpaid(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 3)
    wt.register("ana", 10)
    expect(wt.calc_salary("ana", 0, 1000), 0)
    wt.register("ana", 20)
    expect(wt.calc_salary("ana", 0, 1000), 30)


@case("a worker who never returns keeps the old position and rate")
def promotion_never_used(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    session(wt, "ana", 1, 11)
    expect(wt.promote("ana", "Manager", 50), True)
    expect(wt.top_n_workers(5, "Developer"), ["ana(10)"])
    expect(wt.calc_salary("ana", 0, 100), 100)
    expect(wt.promote("ana", "Director", 90), False, "still pending")


@case("a promotion to the same position with a new rate changes only the rate")
def same_position_new_rate(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    expect(wt.promote("ana", "Developer", 25), True)
    session(wt, "ana", 1, 5)
    expect(wt.calc_salary("ana", 0, 100), 100)
    expect(wt.top_n_workers(5, "Developer"), ["ana(4)"])


@case("a period covering every session pays all of them in full")
def wide_period(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 7)
    session(wt, "ana", 5, 15)
    session(wt, "ana", 100, 103)
    expect(wt.calc_salary("ana", 0, 10**9), 91)
    expect(wt.get_total_time("ana"), 13)


@case("promotions only affect the worker who was promoted")
def promotions_are_per_worker(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    wt.add_worker("ben", "Developer", 10)
    wt.promote("ana", "Senior", 40)
    wt.register("ana", 1)
    wt.register("ben", 2)
    wt.register("ana", 11)
    wt.register("ben", 12)
    expect(wt.calc_salary("ana", 0, 100), 400)
    expect(wt.calc_salary("ben", 0, 100), 100)
    expect(wt.top_n_workers(5, "Developer"), ["ben(10)"])


@case("salaries, promotions and rankings match a tick-by-tick reference model")
def fuzz_against_model(WorkerTimeTracker):
    rng = random.Random(1717)
    wt = WorkerTimeTracker()
    model = {}   # worker id -> position, rate, pending, entered, sessions
    names = ["ana", "ben", "cy", "ghost"]
    positions = ["P0", "P1", "P2"]
    timestamp = 0
    for step in range(600):
        roll = rng.random()
        who = rng.choice(names)
        if roll < 0.08:
            rate = rng.randrange(1, 9)
            ok = who not in model
            expect(wt.add_worker(who, "P0", rate), ok, f"add_worker({who}) at step {step}")
            if ok:
                model[who] = {"position": "P0", "rate": rate, "pending": None,
                              "entered": None, "sessions": []}
        elif roll < 0.55:
            timestamp += rng.randrange(1, 12)
            expect(wt.register(who, timestamp), who in model,
                   f"register({who}, {timestamp}) at step {step}")
            if who in model:
                m = model[who]
                if m["entered"] is None:
                    if m["pending"] is not None:
                        m["position"], m["rate"] = m["pending"]
                        m["pending"] = None
                    m["entered"] = timestamp
                else:
                    m["sessions"].append((m["entered"], timestamp, m["rate"]))
                    m["entered"] = None
        elif roll < 0.68:
            position, rate = rng.choice(positions), rng.randrange(1, 9)
            ok = who in model and model[who]["pending"] is None
            expect(wt.promote(who, position, rate), ok, f"promote({who}) at step {step}")
            if ok:
                model[who]["pending"] = (position, rate)
        elif roll < 0.8:
            position, n = rng.choice(positions), rng.randrange(0, 4)
            totals = {w: sum(leave - enter for enter, leave, _ in m["sessions"])
                      for w, m in model.items()}
            ranked = sorted((w for w in model if model[w]["position"] == position),
                            key=lambda w: (-totals[w], w))
            expect(wt.top_n_workers(n, position), [f"{w}({totals[w]})" for w in ranked[:n]],
                   f"top_n_workers({n}, {position}) at step {step}")
        else:
            start = rng.randrange(0, timestamp + 20)
            end = start + rng.randrange(1, 200)
            want = None
            if who in model:
                want = sum(rate for enter, leave, rate in model[who]["sessions"]
                           for _ in range(max(enter, start), min(leave, end)))
            expect(wt.calc_salary(who, start, end), want,
                   f"calc_salary({who}, {start}, {end}) at step {step}")
