"""Level 2 — the largest files (hidden cases)."""
import random

from icf_testkit import case, expect


@case("n = 0 returns an empty list")
def n_zero(CloudStorage):
    s = CloudStorage()
    s.add_file("a", 1)
    expect(s.get_n_largest("", 0), [])
    expect(s.get_n_largest("", 1), ["a(1)"])


@case("deleted files drop out, copies count as files of their own")
def delete_and_copy(CloudStorage):
    s = CloudStorage()
    s.add_file("log1", 50)
    s.add_file("log2", 60)
    s.copy_file("log2", "log3")
    s.delete_file("log1")
    expect(s.get_n_largest("log", 5), ["log2(60)", "log3(60)"])


@case("the prefix is case-sensitive and may be a whole name")
def prefix_rules(CloudStorage):
    s = CloudStorage()
    s.add_file("Report", 3)
    s.add_file("report", 4)
    s.add_file("report.old", 2)
    expect(s.get_n_largest("report", 5), ["report(4)", "report.old(2)"])
    expect(s.get_n_largest("R", 5), ["Report(3)"])


@case("names tie-break in plain string order")
def string_order(CloudStorage):
    s = CloudStorage()
    for name in ["f10", "f9", "F1", "f1"]:
        s.add_file(name, 7)
    expect(s.get_n_largest("", 4), ["F1(7)", "f1(7)", "f10(7)", "f9(7)"])


@case("a random filesystem matches a sorted reference")
def random_model(CloudStorage):
    rng = random.Random(5)
    s = CloudStorage()
    model = {}
    for step in range(300):
        name = rng.choice("ab") + str(rng.randint(0, 30))
        if rng.random() < 0.7:
            size = rng.randint(0, 20)
            expect(s.add_file(name, size), name not in model)
            model.setdefault(name, size)
        else:
            expect(s.delete_file(name), model.pop(name, None))
        if step % 25 == 0:
            prefix, n = rng.choice(["", "a", "b", "a1"]), rng.randint(0, 8)
            want = sorted((k for k in model if k.startswith(prefix)),
                          key=lambda k: (-model[k], k))[:n]
            expect(s.get_n_largest(prefix, n), [f"{k}({model[k]})" for k in want])
