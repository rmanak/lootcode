"""Level 1 — tasks (hidden cases)."""
import random

from icf_testkit import case, expect


def as_json(name, priority):
    return '{"name":"' + name + '","priority":' + str(priority) + "}"


@case("the id counter keeps counting past nine")
def counter_past_nine(TaskManager):
    tm = TaskManager()
    ids = [tm.add_task(ts, f"t{ts}", ts) for ts in range(1, 13)]
    expect(ids[-1], "task_id_12")
    expect(tm.get_task(20, "task_id_10"), as_json("t10", 10))


@case("a priority of zero or below is written as a plain integer")
def zero_and_negative_priorities(TaskManager):
    tm = TaskManager()
    zero = tm.add_task(1, "x", 0)
    negative = tm.add_task(2, "y", -5)
    expect(tm.get_task(3, zero), '{"name":"x","priority":0}')
    expect(tm.get_task(4, negative), '{"name":"y","priority":-5}')


@case("an update, successful or not, does not use up an id")
def update_keeps_the_counter(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    expect(tm.update_task(2, "task_id_1", "b", 2), True)
    expect(tm.update_task(3, "task_id_7", "c", 3), False)
    expect(tm.add_task(4, "d", 4), "task_id_2")


@case("names are written verbatim, spaces and punctuation included")
def verbatim_names(TaskManager):
    tm = TaskManager()
    name = "Fix bug #42: login (prod), ASAP!"
    task_id = tm.add_task(1, name, 7)
    expect(tm.get_task(2, task_id), as_json(name, 7))


@case("updating a task twice keeps only the latest values")
def repeated_updates(TaskManager):
    tm = TaskManager()
    task_id = tm.add_task(1, "draft", 1)
    expect(tm.update_task(2, task_id, "review", 4), True)
    expect(tm.update_task(3, task_id, "ship", 2), True)
    expect(tm.get_task(4, task_id), as_json("ship", 2))


@case("ids are exact: a near-miss id is not a task")
def ids_are_exact(TaskManager):
    tm = TaskManager()
    tm.add_task(1, "a", 1)
    expect(tm.get_task(2, "task_id_1"), as_json("a", 1))
    for wrong in ("task_id_01", "Task_id_1", "task_1", "1", "task_id_1 "):
        expect(tm.get_task(3, wrong), None, f"{wrong!r} is not an issued id")
        expect(tm.update_task(4, wrong, "b", 2), False, f"{wrong!r} is not an issued id")


@case("a random sequence of adds, updates and reads matches a reference model")
def fuzz_against_model(TaskManager):
    rng = random.Random(4242)
    tm = TaskManager()
    model = {}
    names = ["alpha", "beta", "gamma task", "Delta", "alpha"]
    for ts in range(1, 600):
        roll = rng.random()
        if roll < 0.35:
            name, priority = rng.choice(names), rng.randrange(-3, 10)
            expected_id = f"task_id_{len(model) + 1}"
            expect(tm.add_task(ts, name, priority), expected_id, f"add at ts={ts}")
            model[expected_id] = (name, priority)
        elif roll < 0.65:
            task_id = f"task_id_{rng.randrange(0, len(model) + 3)}"
            name, priority = rng.choice(names), rng.randrange(-3, 10)
            ok = task_id in model
            expect(tm.update_task(ts, task_id, name, priority), ok,
                   f"update {task_id} at ts={ts}")
            if ok:
                model[task_id] = (name, priority)
        else:
            task_id = f"task_id_{rng.randrange(0, len(model) + 3)}"
            want = as_json(*model[task_id]) if task_id in model else None
            expect(tm.get_task(ts, task_id), want, f"get {task_id} at ts={ts}")
