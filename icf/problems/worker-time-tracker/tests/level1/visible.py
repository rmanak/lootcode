"""Level 1 — office attendance (visible cases)."""
from icf_testkit import case, expect


@case("a worker can be added only once")
def add_worker_once(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    expect(wt.add_worker("ana", "Developer", 10), True)
    expect(wt.add_worker("ana", "Manager", 50), False, "the id is taken")


@case("an entry and the following exit form one session")
def one_session(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    expect(wt.register("ana", 10), True, "ana enters")
    expect(wt.register("ana", 25), True, "ana leaves")
    expect(wt.get_total_time("ana"), 15)


@case("register for an unknown worker returns False")
def register_unknown(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    expect(wt.register("ghost", 5), False)
    expect(wt.register("ana", 6), True)


@case("get_total_time adds up every completed session")
def total_of_sessions(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    for timestamp in (10, 25, 40, 100):
        wt.register("ana", timestamp)
    expect(wt.get_total_time("ana"), 75, "[10, 25) and [40, 100)")


@case("a session that is still open does not count yet")
def open_session_excluded(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    wt.register("ana", 10)
    wt.register("ana", 25)
    wt.register("ana", 40)
    expect(wt.get_total_time("ana"), 15, "the session that started at 40 is open")
    wt.register("ana", 100)
    expect(wt.get_total_time("ana"), 75)


@case("a new worker has spent 0, and an unknown worker gives None")
def zero_and_none(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("ana", "Developer", 10)
    expect(wt.get_total_time("ana"), 0)
    expect(wt.get_total_time("ghost"), None)
