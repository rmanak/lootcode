"""Level 3 — users and capacity (hidden cases)."""
import random

from icf_testkit import case, expect


@case("raising the capacity removes nothing and makes room for more")
def raise_capacity(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 100)
    expect(storage.add_file_by("u", "/a", 100), 0)
    expect(storage.update_capacity("u", 300), 0)
    expect(storage.add_file_by("u", "/b", 150), 50)


@case("files added with add_file count against no user's capacity and are never removed")
def admin_files_unlimited(CloudStorage):
    storage = CloudStorage()
    expect(storage.add_file("/big", 10**6), True)
    storage.add_user("u", 10)
    expect(storage.add_file_by("u", "/small", 10), 0)
    expect(storage.update_capacity("u", 0), 1, "only the user's own file is removed")
    expect(storage.get_file_size("/big"), 10**6)
    expect(storage.get_file_size("/small"), None)


@case("a copy that would not fit in its owner's capacity is refused")
def copy_does_not_fit(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 100)
    expect(storage.add_file_by("u", "/a", 60), 40)
    expect(storage.copy_file("/a", "/b"), False)
    expect(storage.get_file_size("/b"), None)
    expect(storage.add_file_by("u", "/c", 40), 0, "the refused copy used nothing")


@case("files removed by update_capacity free their names")
def removal_frees_names(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 100)
    storage.add_file_by("u", "/a", 80)
    expect(storage.update_capacity("u", 50), 1)
    expect(storage.get_file_size("/a"), None)
    expect(storage.add_file_by("u", "/a", 50), 0)


@case("each user's capacity is separate")
def separate_capacities(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u1", 100)
    storage.add_user("u2", 100)
    expect(storage.add_file_by("u1", "/a", 100), 0)
    expect(storage.add_file_by("u2", "/b", 60), 40)
    expect(storage.update_capacity("u1", 50), 1)
    expect(storage.get_file_size("/b"), 60, "u2's file is untouched")


@case("a refused add_user keeps the original capacity")
def refused_add_user(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 10)
    expect(storage.add_user("u", 1000), False)
    expect(storage.add_file_by("u", "/a", 11), None)
    expect(storage.add_file_by("u", "/a", 10), 0)


@case("shrinking the capacity to 0 removes every file the user owns")
def shrink_to_zero(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 100)
    for name, size in (("/a", 30), ("/b", 30), ("/c", 40)):
        storage.add_file_by("u", name, size)
    expect(storage.update_capacity("u", 0), 3)
    expect(storage.find_file("", ""), [])
    expect(storage.add_file_by("u", "/d", 1), None)


@case("update_capacity stops as soon as the remaining files fit")
def stops_early(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 1000)
    storage.add_file_by("u", "/big", 500)
    storage.add_file_by("u", "/s1", 10)
    storage.add_file_by("u", "/s2", 10)
    expect(storage.update_capacity("u", 20), 1)
    expect(storage.get_file_size("/s1"), 10)
    expect(storage.get_file_size("/s2"), 10)


@case("the largest file is removed even when a smaller one would have been enough")
def largest_not_smallest_sufficient(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 110)
    storage.add_file_by("u", "/large", 100)
    storage.add_file_by("u", "/tiny", 10)
    expect(storage.update_capacity("u", 105), 1)
    expect(storage.get_file_size("/large"), None)
    expect(storage.get_file_size("/tiny"), 10)


@case("a lower capacity stays in force for later additions")
def lower_capacity_persists(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 1000)
    storage.add_file_by("u", "/a", 20)
    expect(storage.update_capacity("u", 50), 0)
    expect(storage.add_file_by("u", "/b", 31), None)
    expect(storage.add_file_by("u", "/b", 30), 0)


@case("copying a file added with add_file makes another unlimited file")
def copy_admin_file(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 0)
    storage.add_file("/x", 50)
    expect(storage.copy_file("/x", "/y"), True)
    expect(storage.update_capacity("u", 0), 0)
    expect(storage.get_file_size("/y"), 50)


@case("files of every owner appear in find_file")
def find_sees_all_owners(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u1", 100)
    storage.add_user("u2", 100)
    storage.add_file("/shared/admin.txt", 7)
    storage.add_file_by("u1", "/shared/one.txt", 7)
    storage.add_file_by("u2", "/shared/two.txt", 9)
    expect(storage.find_file("/shared/", ".txt"),
           ["/shared/two.txt(9)", "/shared/admin.txt(7)", "/shared/one.txt(7)"])


@case("capacity rules match a reference model over a random workload")
def fuzz_against_model(CloudStorage):
    rng = random.Random(8642)
    storage = CloudStorage()
    files = {}   # name -> [size, owner]
    caps = {}
    names = ["/a", "/b", "/c", "/d/e", "/d/f", "/g", "/h"]

    def used(user):
        return sum(size for size, owner in files.values() if owner == user)

    for step in range(900):
        roll = rng.random()
        user = rng.choice(["u1", "u2", "u3"])
        name = rng.choice(names)
        if roll < 0.08:
            capacity = rng.randrange(0, 300)
            ok = user not in caps
            expect(storage.add_user(user, capacity), ok, f"add_user({user}) at step {step}")
            if ok:
                caps[user] = capacity
        elif roll < 0.15:
            size = rng.randrange(1, 80)
            ok = name not in files
            expect(storage.add_file(name, size), ok, f"add_file({name}) at step {step}")
            if ok:
                files[name] = [size, "admin"]
        elif roll < 0.4:
            size = rng.randrange(1, 120)
            ok = user in caps and name not in files and used(user) + size <= caps[user]
            want = caps[user] - used(user) - size if ok else None
            expect(storage.add_file_by(user, name, size), want,
                   f"add_file_by({user}, {name}, {size}) at step {step}")
            if ok:
                files[name] = [size, user]
        elif roll < 0.55:
            source, target = rng.choice(names), rng.choice(names)
            ok = source in files and target not in files
            if ok:
                size, owner = files[source]
                ok = owner == "admin" or used(owner) + size <= caps[owner]
            expect(storage.copy_file(source, target), ok,
                   f"copy_file({source}, {target}) at step {step}")
            if ok:
                files[target] = list(files[source])
        elif roll < 0.65:
            capacity = rng.randrange(0, 300)
            want = None
            if user in caps:
                caps[user] = capacity
                want = 0
                for owned in sorted((n for n in files if files[n][1] == user),
                                    key=lambda n: (-files[n][0], n)):
                    if used(user) <= capacity:
                        break
                    del files[owned]
                    want += 1
            expect(storage.update_capacity(user, capacity), want,
                   f"update_capacity({user}, {capacity}) at step {step}")
        elif roll < 0.85:
            expect(storage.get_file_size(name), files[name][0] if name in files else None,
                   f"get_file_size({name}) at step {step}")
        else:
            ranked = sorted(files, key=lambda n: (-files[n][0], n))
            expect(storage.find_file("", ""), [f"{n}({files[n][0]})" for n in ranked],
                   f"find_file at step {step}")
