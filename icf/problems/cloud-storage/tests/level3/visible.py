"""Level 3 — users and capacity (visible cases)."""
from icf_testkit import case, expect


@case("a user can only be added once")
def add_user_once(CloudStorage):
    storage = CloudStorage()
    expect(storage.add_user("user1", 200), True)
    expect(storage.add_user("user1", 100), False)
    expect(storage.add_user("user2", 100), True)


@case("add_file_by returns the user's remaining capacity, down to exactly 0")
def remaining_capacity(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 200)
    expect(storage.add_file_by("user1", "/dir/file.big", 100), 100)
    expect(storage.add_file_by("user1", "/file.med", 70), 30)
    expect(storage.add_file_by("user1", "/file.small", 30), 0, "an exact fit is allowed")
    expect(storage.get_file_size("/file.med"), 70)


@case("add_file_by is refused for an unknown user, a taken name, or a file that does not fit")
def add_file_by_refused(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 100)
    storage.add_file("/taken", 5)
    expect(storage.add_file_by("user3", "/a", 10), None, "no such user")
    expect(storage.add_file_by("user1", "/taken", 10), None, "the name exists")
    expect(storage.add_file_by("user1", "/a", 101), None, "more than the capacity")
    expect(storage.get_file_size("/a"), None, "nothing was added")
    expect(storage.add_file_by("user1", "/a", 100), 0, "the refusals used no capacity")


@case("a copy belongs to the owner of the original and uses their capacity")
def copy_keeps_owner(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 100)
    expect(storage.add_file_by("user1", "/a", 30), 70)
    expect(storage.copy_file("/a", "/b"), True)
    expect(storage.add_file_by("user1", "/c", 41), None, "only 40 bytes are left")
    expect(storage.add_file_by("user1", "/c", 40), 0)


@case("update_capacity removes the largest files first, breaking ties by name")
def update_removes_largest(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 200)
    storage.add_file_by("user1", "/big", 100)
    storage.add_file_by("user1", "/med-b", 30)
    storage.add_file_by("user1", "/med-a", 30)
    storage.add_file_by("user1", "/small", 10)
    expect(storage.update_capacity("user1", 45), 2)
    expect(storage.get_file_size("/big"), None)
    expect(storage.get_file_size("/med-a"), None, "removed before /med-b")
    expect(storage.get_file_size("/med-b"), 30)
    expect(storage.get_file_size("/small"), 10)


@case("update_capacity returns 0 when everything fits, and None for an unknown user")
def update_trivial(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 100)
    storage.add_file_by("user1", "/a", 60)
    expect(storage.update_capacity("user1", 60), 0)
    expect(storage.update_capacity("ghost", 10), None)
    expect(storage.get_file_size("/a"), 60)
