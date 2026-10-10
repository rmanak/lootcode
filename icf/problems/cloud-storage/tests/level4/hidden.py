"""Level 4 — compression (hidden cases)."""
import random

from icf_testkit import case, expect

SUFFIX = ".COMPRESSED"


@case("a compressed file can be copied, and the copy decompressed under its own name")
def copy_compressed(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 1000)
    storage.add_file_by("user1", "/dir/file.mp4", 500)
    expect(storage.compress_file("user1", "/dir/file.mp4"), 750)
    expect(storage.copy_file("/dir/file.mp4.COMPRESSED", "/file.mp4.COMPRESSED"), True)
    expect(storage.add_file_by("user1", "/dir/file.mp4", 500), 0)
    expect(storage.update_capacity("user1", 2000), 0)
    expect(storage.decompress_file("user1", "/file.mp4.COMPRESSED"), 750)
    expect(storage.get_file_size("/file.mp4"), 500)
    expect(storage.get_file_size("/dir/file.mp4.COMPRESSED"), 250)


@case("compression is refused when the compressed name is already taken")
def compressed_name_taken(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 1000)
    storage.add_file_by("u", "/a", 100)
    expect(storage.compress_file("u", "/a"), 950)
    expect(storage.add_file_by("u", "/a", 200), 750)
    expect(storage.compress_file("u", "/a"), None)
    expect(storage.get_file_size("/a"), 200)
    expect(storage.get_file_size("/a.COMPRESSED"), 50)


@case("only a file whose name ends with .COMPRESSED can be decompressed")
def decompress_needs_suffix(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 1000)
    storage.add_file_by("u", "/plain", 100)
    storage.add_file_by("u", "/packed", 100)
    storage.compress_file("u", "/packed")
    expect(storage.decompress_file("u", "/plain"), None, "not a compressed file")
    expect(storage.decompress_file("u", "/packed"), None,
           "the name must include the suffix, and /packed no longer exists")
    expect(storage.get_file_size("/plain"), 100)
    expect(storage.decompress_file("u", "/packed.COMPRESSED"), 800)


@case("decompression is refused for an unknown user, a missing file, or another user's file")
def decompress_refused(CloudStorage):
    storage = CloudStorage()
    storage.add_user("ana", 100)
    storage.add_user("ben", 100)
    storage.add_file_by("ana", "/a", 40)
    expect(storage.compress_file("ana", "/a"), 80)
    expect(storage.decompress_file("ghost", "/a.COMPRESSED"), None)
    expect(storage.decompress_file("ben", "/a.COMPRESSED"), None)
    expect(storage.decompress_file("ana", "/zzz.COMPRESSED"), None)
    expect(storage.decompress_file("ana", "/a.COMPRESSED"), 60)


@case("compressed files appear in find_file and are removed by update_capacity like any other")
def compressed_files_are_files(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 1000)
    storage.add_file_by("u", "/big", 600)
    storage.add_file_by("u", "/small", 100)
    expect(storage.compress_file("u", "/big"), 600)
    expect(storage.find_file("/", ""), ["/big.COMPRESSED(300)", "/small(100)"])
    expect(storage.find_file("", SUFFIX), ["/big.COMPRESSED(300)"])
    expect(storage.update_capacity("u", 150), 1)
    expect(storage.get_file_size("/big.COMPRESSED"), None)
    expect(storage.get_file_size("/small"), 100)


@case("a file can be compressed and decompressed again and again")
def repeated_round_trips(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 100)
    storage.add_file_by("u", "/a", 40)
    for _ in range(3):
        expect(storage.compress_file("u", "/a"), 80)
        expect(storage.decompress_file("u", "/a.COMPRESSED"), 60)
    expect(storage.get_file_size("/a"), 40)


@case("files added with add_file cannot be compressed by a user")
def admin_files_not_compressible(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 100)
    storage.add_file("/x", 10)
    expect(storage.compress_file("u", "/x"), None)
    expect(storage.get_file_size("/x"), 10)
    expect(storage.add_file_by("u", "/y", 10), 90)
    expect(storage.compress_file("u", "/y"), 95)


@case("decompression that exactly fills the capacity is allowed")
def decompress_exact_fit(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 100)
    expect(storage.add_file_by("u", "/a", 100), 0)
    expect(storage.compress_file("u", "/a"), 50)
    expect(storage.decompress_file("u", "/a.COMPRESSED"), 0)


@case("a refused decompression leaves the capacity where it was")
def refused_decompress_is_inert(CloudStorage):
    storage = CloudStorage()
    storage.add_user("u", 300)
    storage.add_file_by("u", "/a", 200)
    storage.compress_file("u", "/a")
    storage.add_file_by("u", "/b", 150)
    expect(storage.decompress_file("u", "/a.COMPRESSED"), None)
    expect(storage.add_file_by("u", "/c", 50), 0, "100 + 150 + 50 = 300")


@case("compression, decompression and capacity match a reference model over a random workload")
def fuzz_against_model(CloudStorage):
    rng = random.Random(3131)
    storage = CloudStorage()
    files = {}   # name -> [size, owner]
    caps = {}
    bases = ["/a", "/b", "/c", "/d/x", "/d/y"]

    def used(user):
        return sum(size for size, owner in files.values() if owner == user)

    for step in range(1000):
        roll = rng.random()
        user = rng.choice(["u1", "u2", "ghost"])
        base = rng.choice(bases)
        if roll < 0.08:
            capacity = rng.randrange(0, 400)
            ok = user not in caps
            expect(storage.add_user(user, capacity), ok, f"add_user({user}) at step {step}")
            if ok:
                caps[user] = capacity
        elif roll < 0.14:
            size = rng.randrange(1, 40) * 2
            ok = base not in files
            expect(storage.add_file(base, size), ok, f"add_file({base}) at step {step}")
            if ok:
                files[base] = [size, "admin"]
        elif roll < 0.34:
            size = rng.randrange(1, 60) * 2
            ok = user in caps and base not in files and used(user) + size <= caps[user]
            want = caps[user] - used(user) - size if ok else None
            expect(storage.add_file_by(user, base, size), want,
                   f"add_file_by({user}, {base}, {size}) at step {step}")
            if ok:
                files[base] = [size, user]
        elif roll < 0.44:
            source = rng.choice(sorted(files)) if files and rng.random() < 0.8 else base
            target = rng.choice(bases) + (SUFFIX if source.endswith(SUFFIX) else "")
            ok = source in files and target not in files
            if ok:
                size, owner = files[source]
                ok = owner == "admin" or used(owner) + size <= caps[owner]
            expect(storage.copy_file(source, target), ok,
                   f"copy_file({source}, {target}) at step {step}")
            if ok:
                files[target] = list(files[source])
        elif roll < 0.52:
            capacity = rng.randrange(0, 400)
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
        elif roll < 0.68:
            # compress_file is never called on a name that already ends with the suffix.
            plain = [n for n in sorted(files) if not n.endswith(SUFFIX)]
            name = rng.choice(plain) if plain and rng.random() < 0.8 else base
            file = files.get(name)
            ok = (user in caps and file is not None and file[1] == user
                  and name + SUFFIX not in files)
            want = None
            if ok:
                del files[name]
                files[name + SUFFIX] = [file[0] // 2, user]
                want = caps[user] - used(user)
            expect(storage.compress_file(user, name), want,
                   f"compress_file({user}, {name}) at step {step}")
        elif roll < 0.84:
            compressed = [n for n in sorted(files) if n.endswith(SUFFIX)]
            pool = compressed if compressed and rng.random() < 0.75 else sorted(files) + [base + SUFFIX]
            name = rng.choice(pool)
            file = files.get(name)
            original = name[:-len(SUFFIX)] if name.endswith(SUFFIX) else None
            ok = (user in caps and file is not None and file[1] == user
                  and original is not None and original not in files
                  and used(user) + file[0] <= caps[user])
            want = None
            if ok:
                del files[name]
                files[original] = [file[0] * 2, user]
                want = caps[user] - used(user)
            expect(storage.decompress_file(user, name), want,
                   f"decompress_file({user}, {name}) at step {step}")
        elif roll < 0.92:
            name = rng.choice(sorted(files) + [base, base + SUFFIX])
            expect(storage.get_file_size(name), files[name][0] if name in files else None,
                   f"get_file_size({name}) at step {step}")
        else:
            prefix = rng.choice(["", "/a", "/d/", "/"])
            suffix = rng.choice(["", SUFFIX, "a", "y"])
            matches = sorted((n for n in files if n.startswith(prefix) and n.endswith(suffix)),
                             key=lambda n: (-files[n][0], n))
            expect(storage.find_file(prefix, suffix), [f"{n}({files[n][0]})" for n in matches],
                   f"find_file({prefix!r}, {suffix!r}) at step {step}")
