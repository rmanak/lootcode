"""Level 2 — ranking by time (hidden cases)."""
import random

from icf_testkit import case, expect


def session(wt, worker_id, enter, leave):
    wt.register(worker_id, enter)
    wt.register(worker_id, leave)


@case("a worker who has never completed a session is listed with 0")
def never_worked_listed(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("a", "Developer", 10)
    wt.add_worker("b", "Developer", 10)
    wt.add_worker("c", "Developer", 10)
    session(wt, "a", 1, 11)
    wt.register("b", 20)   # still inside
    expect(wt.top_n_workers(5, "Developer"), ["a(10)", "b(0)", "c(0)"])


@case("a position nobody holds gives an empty list")
def empty_position(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("a", "Developer", 10)
    expect(wt.top_n_workers(5, "Developer"), ["a(0)"])
    expect(wt.top_n_workers(5, "Astronaut"), [])


@case("an open session does not count towards the ranking")
def open_session_not_ranked(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("a", "Developer", 10)
    wt.add_worker("b", "Developer", 10)
    session(wt, "a", 1, 11)
    session(wt, "b", 12, 22)
    wt.register("a", 30)
    expect(wt.top_n_workers(2, "Developer"), ["a(10)", "b(10)"])
    wt.register("a", 100)
    expect(wt.top_n_workers(2, "Developer"), ["a(80)", "b(10)"])


@case("ids compare as strings, so w10 comes before w9")
def ids_as_strings(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("w9", "Developer", 10)
    wt.add_worker("w10", "Developer", 10)
    session(wt, "w9", 1, 11)
    session(wt, "w10", 20, 30)
    expect(wt.top_n_workers(2, "Developer"), ["w10(10)", "w9(10)"])


@case("n of 0 gives an empty list")
def n_zero(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("a", "Developer", 10)
    expect(wt.top_n_workers(1, "Developer"), ["a(0)"])
    expect(wt.top_n_workers(0, "Developer"), [])


@case("positions are matched exactly, including case")
def positions_exact(WorkerTimeTracker):
    wt = WorkerTimeTracker()
    wt.add_worker("a", "Dev", 10)
    wt.add_worker("b", "dev", 10)
    wt.add_worker("c", "Dev ", 10)
    expect(wt.top_n_workers(5, "Dev"), ["a(0)"])
    expect(wt.top_n_workers(5, "dev"), ["b(0)"])


@case("the ranking matches a reference model over a random workload")
def fuzz_against_model(WorkerTimeTracker):
    rng = random.Random(606)
    wt = WorkerTimeTracker()
    positions, totals, entered = {}, {}, {}
    names = [f"w{i}" for i in range(12)]
    kinds = ["Developer", "Designer", "Manager"]
    timestamp = 0
    for step in range(900):
        roll = rng.random()
        who = rng.choice(names)
        if roll < 0.15:
            position = rng.choice(kinds)
            expect(wt.add_worker(who, position, 10), who not in positions,
                   f"add_worker({who}) at step {step}")
            if who not in positions:
                positions[who], totals[who] = position, 0
        elif roll < 0.75:
            timestamp += rng.randrange(1, 15)
            wt.register(who, timestamp)
            if who in positions:
                if who in entered:
                    totals[who] += timestamp - entered.pop(who)
                else:
                    entered[who] = timestamp
        else:
            position, n = rng.choice(kinds), rng.randrange(0, 6)
            ranked = sorted((w for w in positions if positions[w] == position),
                            key=lambda w: (-totals[w], w))
            want = [f"{w}({totals[w]})" for w in ranked[:n]]
            expect(wt.top_n_workers(n, position), want,
                   f"top_n_workers({n}, {position}) at step {step}")
