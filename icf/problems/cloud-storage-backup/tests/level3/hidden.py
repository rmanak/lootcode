"""Level 3 — users, capacity and merging (hidden cases)."""
from icf_testkit import case, expect


@case("the administrator owns add_file's files and has no limit")
def admin(CloudStorage):
    s = CloudStorage()
    expect(s.add_user("admin", 10), False, "admin always exists")
    s.add_file("big", 10 ** 12)
    expect(s.copy_file("big", "big2"), True)
    expect(s.add_file_by("admin", "x", 1), None, "admin is not a regular user")


@case("merges involving admin, unknown users or the same user are refused")
def merge_refused(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 10)
    s.add_file("a", 5)
    expect(s.merge_user("u1", "u1"), None)
    expect(s.merge_user("u1", "admin"), None)
    expect(s.merge_user("admin", "u1"), None)
    expect(s.merge_user("u1", "zed"), None)
    expect(s.add_file_by("u1", "b", 10), 0, "u1 unchanged")


@case("merged files count against the new owner and copies follow")
def merged_files_owned(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 10)
    s.add_user("u2", 10)
    s.add_file_by("u2", "b", 8)
    s.merge_user("u1", "u2")
    expect(s.copy_file("b", "b2"), True, "20 capacity, 16 used")
    expect(s.copy_file("b", "b3"), False)
    expect(s.delete_file("b"), 8)
    expect(s.add_file_by("u1", "c", 12), 0)


@case("a merged-away id can be added again as a brand-new user")
def readd(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 10)
    s.add_user("u2", 10)
    s.add_file_by("u2", "b", 5)
    s.merge_user("u1", "u2")
    expect(s.add_user("u2", 3), True)
    expect(s.add_file_by("u2", "c", 3), 0, "the new u2 owns nothing")


@case("a failed add_file_by or copy changes nothing")
def failures_change_nothing(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 5)
    s.add_file_by("u1", "a", 4)
    expect(s.add_file_by("u1", "b", 2), None)
    expect(s.get_file_size("b"), None)
    expect(s.copy_file("a", "a2"), False)
    expect(s.get_file_size("a2"), None)
    expect(s.add_file_by("u1", "c", 1), 0)


@case("the largest-files listing sees every owner's files")
def listing_all_owners(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_file("x1", 7)
    s.add_file_by("u1", "x2", 9)
    expect(s.get_n_largest("x", 5), ["x2(9)", "x1(7)"])
