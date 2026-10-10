"""Level 1 — files (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a refused copy changes neither file")
def refused_copy_is_inert(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a", 10)
    storage.add_file("/b", 20)
    expect(storage.copy_file("/a", "/b"), False)
    expect(storage.get_file_size("/a"), 10)
    expect(storage.get_file_size("/b"), 20)


@case("a copy of a copy is another separate file")
def copy_of_copy(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a", 7)
    expect(storage.copy_file("/a", "/b"), True)
    expect(storage.copy_file("/b", "/c"), True)
    expect(storage.get_file_size("/c"), 7)
    expect(storage.add_file("/c", 1), False, "the copy is a real file")
    expect(storage.copy_file("/a", "/c"), False)


@case("copying a file onto itself is refused")
def copy_onto_itself(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a", 5)
    expect(storage.copy_file("/a", "/a"), False)
    expect(storage.get_file_size("/a"), 5)


@case("a directory name has no size")
def directory_has_no_size(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/photos/2024/beach.png", 300)
    expect(storage.get_file_size("/photos/2024"), None)
    expect(storage.get_file_size("/photos"), None)
    expect(storage.get_file_size("/photos/2024/beach.png"), 300)


@case("a file may be copied into a directory that has no files yet")
def copy_into_new_directory(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/docs/report.pdf", 64)
    expect(storage.copy_file("/docs/report.pdf", "/archive/2024/report.pdf"), True)
    expect(storage.get_file_size("/archive/2024/report.pdf"), 64)
    expect(storage.copy_file("/archive/2024", "/archive/copy"), False,
           "the new directory is still not a file")


@case("names are case-sensitive and compared whole")
def names_exact(CloudStorage):
    storage = CloudStorage()
    expect(storage.add_file("/File.txt", 1), True)
    expect(storage.add_file("/file.txt", 2), True, "a different name")
    expect(storage.get_file_size("/File.txt"), 1)
    expect(storage.get_file_size("/file.tx"), None)
    expect(storage.get_file_size("/file.txt "), None)


@case("large sizes are stored exactly")
def large_sizes(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/disk.img", 10**12 + 7)
    storage.copy_file("/disk.img", "/disk-copy.img")
    expect(storage.get_file_size("/disk-copy.img"), 10**12 + 7)


@case("adds, copies and reads match a reference model over a random workload")
def fuzz_against_model(CloudStorage):
    rng = random.Random(2468)
    storage = CloudStorage()
    model = {}
    names = ["/a", "/b", "/A", "/d/x", "/d/y", "/e/f/g", "/e/h"]
    directories = ["/d", "/e", "/e/f"]
    for step in range(600):
        roll = rng.random()
        if roll < 0.35:
            name, size = rng.choice(names), rng.randrange(1, 100)
            ok = name not in model
            expect(storage.add_file(name, size), ok, f"add_file({name}) at step {step}")
            if ok:
                model[name] = size
        elif roll < 0.65:
            source, target = rng.choice(names + directories), rng.choice(names)
            ok = source in model and target not in model
            expect(storage.copy_file(source, target), ok,
                   f"copy_file({source}, {target}) at step {step}")
            if ok:
                model[target] = model[source]
        else:
            name = rng.choice(names + directories)
            expect(storage.get_file_size(name), model.get(name),
                   f"get_file_size({name}) at step {step}")
