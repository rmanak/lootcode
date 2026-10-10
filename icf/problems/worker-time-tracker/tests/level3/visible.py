"""Level 3 — promotions and salary (visible cases)."""
from icf_testkit import case, expect


def session(wt, worker_id, enter, leave):
    wt.register(worker_id, enter)
    wt.register(worker_id, leave)


@case("a promotion takes effect only at the worker's next entry")
def promotion_waits_for_entry(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Junior", 10)
    session(wt, "ana", 100, 200)
    expect(wt.promote("ana", "Senior", 20), True)
    expect(wt.top_n_workers(5, "Junior"), ["ana(100)"], "not in effect yet")
    expect(wt.top_n_workers(5, "Senior"), [])
    wt.register("ana", 300)
    expect(wt.top_n_workers(5, "Senior"), ["ana(100)"], "took effect when ana entered")
    expect(wt.top_n_workers(5, "Junior"), [])


@case("calc_salary pays each session at the rate the worker had when it started")
def rate_per_session(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Junior", 10)
    session(wt, "ana", 100, 200)
    wt.promote("ana", "Senior", 20)
    session(wt, "ana", 300, 400)
    expect(wt.calc_salary("ana", 0, 500), 3000, "100 × 10 + 100 × 20")
    expect(wt.calc_salary("ana", 0, 250), 1000, "only the first session")


@case("a promotion made during a session does not change that session's pay")
def promotion_mid_session(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Junior", 10)
    wt.register("ana", 10)
    expect(wt.promote("ana", "Senior", 30), True)
    wt.register("ana", 20)
    expect(wt.calc_salary("ana", 0, 100), 100, "[10, 20) is still paid at 10")
    session(wt, "ana", 30, 40)
    expect(wt.calc_salary("ana", 0, 100), 400, "then [30, 40) at 30")


@case("calc_salary counts only the part of each session inside the period")
def partial_overlap(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 2)
    session(wt, "ana", 10, 50)
    expect(wt.calc_salary("ana", 20, 40), 40)
    expect(wt.calc_salary("ana", 0, 30), 40)
    expect(wt.calc_salary("ana", 45, 100), 10)
    expect(wt.calc_salary("ana", 60, 70), 0)
    expect(wt.calc_salary("ana", 0, 100), 80)


@case("promote and calc_salary refuse an unknown worker")
def unknown_worker(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    expect(wt.promote("ghost", "Senior", 20), False)
    expect(wt.calc_salary("ghost", 0, 10), None)
    expect(wt.promote("ana", "Senior", 20), True)
    expect(wt.calc_salary("ana", 0, 10), 0)
