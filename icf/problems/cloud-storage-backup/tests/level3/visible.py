"""Level 3 — users, capacity and merging (visible cases)."""
from icf_testkit import case, expect


@case("a user is created once")
def add_user(CloudStorage):
    s = CloudStorage()
    expect(s.add_user("u1", 100), True)
    expect(s.add_user("u1", 500), False)
    expect(s.add_file_by("u1", "f", 100), 0, "the capacity is still 100")


@case("add_file_by returns the remaining capacity, and refuses what doesn't fit")
def add_file_by(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    expect(s.add_file_by("u1", "a", 30), 70)
    expect(s.add_file_by("u1", "b", 80), None, "only 70 left")
    expect(s.add_file_by("u1", "b", 70), 0, "exactly full is fine")
    expect(s.add_file_by("nobody", "c", 1), None)
    expect(s.add_file_by("u1", "a", 0), None, "the name is taken")


@case("deleting a file frees its owner's capacity")
def delete_frees(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 10)
    s.add_file_by("u1", "a", 10)
    expect(s.delete_file("a"), 10)
    expect(s.add_file_by("u1", "b", 10), 0)


@case("a copy belongs to the source's owner and must fit")
def copy_owner(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 50)
    s.add_file_by("u1", "a", 20)
    expect(s.copy_file("a", "b"), True)
    expect(s.copy_file("a", "c"), False, "a third 20 would exceed 50")
    expect(s.add_file_by("u1", "d", 10), 0)


@case("merging adds capacity and files, and removes the second user")
def merge(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_user("u2", 50)
    s.add_file_by("u1", "a", 30)
    s.add_file_by("u2", "b", 40)
    expect(s.merge_user("u1", "u2"), 80, "150 capacity - 70 used")
    expect(s.add_file_by("u2", "c", 1), None, "u2 is gone")
    expect(s.add_file_by("u1", "c", 80), 0)
