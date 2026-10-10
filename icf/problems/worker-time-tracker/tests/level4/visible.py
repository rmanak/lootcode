"""Level 4 — double-pay periods (visible cases)."""
from icf_testkit import case, expect


def session(wt, worker_id, enter, leave):
    wt.register(worker_id, enter)
    wt.register(worker_id, leave)


@case("time inside a double-pay period is paid twice")
def doubled_time(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("e1", "Junior", 10)
    session(wt, "e1", 100, 200)
    wt.promote("e1", "Senior", 20)
    session(wt, "e1", 300, 400)
    wt.set_double_pay(350, 450)
    expect(wt.calc_salary("e1", 0, 500), 4000,
           "100 × 10, then 50 × 20 and 50 × 40")


@case("double pay also applies to sessions that happened before it was declared")
def retroactive_double_pay(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 5)
    session(wt, "ana", 10, 20)
    expect(wt.calc_salary("ana", 0, 100), 50)
    wt.set_double_pay(0, 15)
    expect(wt.calc_salary("ana", 0, 100), 75)


@case("overlapping double-pay periods never pay more than double")
def overlaps_do_not_stack(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 1)
    session(wt, "ana", 0, 200)
    wt.set_double_pay(0, 100)
    wt.set_double_pay(50, 150)
    expect(wt.calc_salary("ana", 0, 200), 350, "200 at 1, plus 150 doubled — not 200")


@case("double pay applies to every worker")
def every_worker(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    wt.add_worker("ben", "Designer", 1)
    wt.register("ana", 10)
    wt.register("ben", 12)
    wt.register("ana", 20)
    wt.register("ben", 22)
    wt.set_double_pay(15, 25)
    expect(wt.calc_salary("ana", 0, 100), 150)
    expect(wt.calc_salary("ben", 0, 100), 17)
