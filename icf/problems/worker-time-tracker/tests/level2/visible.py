"""Level 2 — ranking by time (visible cases)."""
from icf_testkit import case, expect


def session(wt, worker_id, enter, leave):
    wt.register(worker_id, enter)
    wt.register(worker_id, leave)


@case("top_n_workers ranks a position's workers by time in the office")
def ranks_by_time(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    for worker_id in ("a", "b", "c"):
        wt.add_worker(worker_id, "Developer", 10)
    session(wt, "a", 1, 31)
    session(wt, "b", 40, 90)
    session(wt, "c", 100, 110)
    expect(wt.top_n_workers(3, "Developer"), ["b(50)", "a(30)", "c(10)"])


@case("only workers holding the requested position are ranked")
def only_that_position(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("a", "Developer", 10)
    wt.add_worker("d", "Designer", 10)
    session(wt, "a", 1, 31)
    session(wt, "d", 40, 140)
    expect(wt.top_n_workers(5, "Developer"), ["a(30)"])
    expect(wt.top_n_workers(5, "Designer"), ["d(100)"])


@case("workers with the same time are ordered by id")
def ties_by_id(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    for worker_id in ("c", "b", "a"):
        wt.add_worker(worker_id, "Developer", 10)
    session(wt, "b", 1, 21)
    session(wt, "a", 30, 50)
    session(wt, "c", 60, 65)
    expect(wt.top_n_workers(3, "Developer"), ["a(20)", "b(20)", "c(5)"])


@case("n caps the ranking, and asking for more than exist returns everyone")
def n_caps(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    for worker_id in ("a", "b", "c"):
        wt.add_worker(worker_id, "Developer", 10)
    session(wt, "a", 1, 4)
    session(wt, "b", 10, 12)
    session(wt, "c", 20, 21)
    expect(wt.top_n_workers(2, "Developer"), ["a(3)", "b(2)"])
    expect(wt.top_n_workers(10, "Developer"), ["a(3)", "b(2)", "c(1)"])
