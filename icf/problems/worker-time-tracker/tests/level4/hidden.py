"""Level 4 — double-pay periods (hidden cases)."""
import random

from icf_testkit import case, expect


def session(wt, worker_id, enter, leave):
    wt.register(worker_id, enter)
    wt.register(worker_id, leave)


@case("a period that only touches a session changes nothing")
def touching_periods(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 5)
    session(wt, "ana", 10, 20)
    wt.set_double_pay(20, 30)
    wt.set_double_pay(0, 10)
    expect(wt.calc_salary("ana", 0, 100), 50)


@case("a period inside a session, seen through a salary period that cuts it")
def cut_by_salary_period(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 3)
    session(wt, "ana", 0, 100)
    wt.set_double_pay(40, 60)
    expect(wt.calc_salary("ana", 50, 200), 180, "50 × 3, plus [50, 60) doubled")
    expect(wt.calc_salary("ana", 0, 100), 360)


@case("declaring the same period twice counts it once")
def same_period_twice(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 2)
    session(wt, "ana", 0, 10)
    wt.set_double_pay(0, 5)
    wt.set_double_pay(0, 5)
    expect(wt.calc_salary("ana", 0, 10), 30)


@case("a period nested inside another adds nothing")
def nested_period(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 1)
    session(wt, "ana", 0, 100)
    wt.set_double_pay(10, 90)
    wt.set_double_pay(20, 30)
    expect(wt.calc_salary("ana", 0, 100), 180)


@case("adjacent periods double every unit of time they cover")
def adjacent_periods(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 1)
    session(wt, "ana", 0, 40)
    wt.set_double_pay(10, 20)
    wt.set_double_pay(20, 30)
    expect(wt.calc_salary("ana", 0, 40), 60)


@case("double pay multiplies the rate each session was paid at")
def doubles_promoted_rate(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Junior", 10)
    session(wt, "ana", 0, 10)
    wt.promote("ana", "Senior", 20)
    session(wt, "ana", 20, 30)
    wt.set_double_pay(5, 25)
    expect(wt.calc_salary("ana", 0, 100), 450, "(100 + 5 × 10) + (200 + 5 × 20)")


@case("double pay does not change time in the office or the ranking")
def time_unaffected(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 1)
    session(wt, "ana", 0, 10)
    wt.set_double_pay(0, 10)
    expect(wt.get_total_time("ana"), 10)
    expect(wt.top_n_workers(1, "Developer"), ["ana(10)"])
    expect(wt.calc_salary("ana", 0, 10), 20)


@case("a period that bridges two earlier periods is not counted twice")
def bridging_period(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 1)
    session(wt, "ana", 0, 40)
    wt.set_double_pay(0, 10)
    wt.set_double_pay(20, 30)
    wt.set_double_pay(5, 25)
    expect(wt.calc_salary("ana", 0, 40), 70, "together they cover [0, 30)")


@case("salaries with double pay match a tick-by-tick reference model")
def fuzz_against_model(WorkerTimeTracker):
    rng = random.Random(8080)
    wt = WorkerTimeTracker()
    rates = {"ana": 3, "ben": 7, "cy": 1}
    sessions = {name: [] for name in rates}
    entered = {}
    periods = []
    for name, rate in rates.items():
        expect(wt.add_worker(name, "Developer", rate), True)
    timestamp = 0
    for step in range(400):
        roll = rng.random()
        who = rng.choice(list(rates))
        if roll < 0.55:
            timestamp += rng.randrange(1, 10)
            wt.register(who, timestamp)
            if who in entered:
                sessions[who].append((entered.pop(who), timestamp))
            else:
                entered[who] = timestamp
        elif roll < 0.7:
            start = rng.randrange(0, timestamp + 30)
            end = start + rng.randrange(1, 60)
            wt.set_double_pay(start, end)
            periods.append((start, end))
        else:
            start = rng.randrange(0, timestamp + 10)
            end = start + rng.randrange(1, 150)
            want = 0
            for enter, leave in sessions[who]:
                for tick in range(max(enter, start), min(leave, end)):
                    doubled = any(s <= tick < e for s, e in periods)
                    want += rates[who] * (2 if doubled else 1)
            expect(wt.calc_salary(who, start, end), want,
                   f"calc_salary({who}, {start}, {end}) at step {step}")
