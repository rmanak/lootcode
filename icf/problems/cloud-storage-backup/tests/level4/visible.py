"""Level 4 — backup and restore (visible cases)."""
from icf_testkit import case, expect


@case("backup counts the user's files")
def backup_count(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_file_by("u1", "a", 10)
    s.add_file_by("u1", "b", 20)
    s.add_file("admin_file", 5)
    expect(s.backup_user("u1"), 2)
    expect(s.backup_user("zed"), None)


@case("restore brings back deleted files and removes newer ones")
def restore(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_file_by("u1", "a", 10)
    s.add_file_by("u1", "b", 20)
    s.backup_user("u1")
    s.delete_file("a")
    s.add_file_by("u1", "c", 30)
    expect(s.restore_user("u1"), 2)
    expect(s.get_file_size("a"), 10)
    expect(s.get_file_size("b"), 20)
    expect(s.get_file_size("c"), None, "not in the backup")


@case("a file whose name now belongs to someone else is skipped")
def skip_taken(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_file_by("u1", "a", 10)
    s.add_file_by("u1", "b", 10)
    s.backup_user("u1")
    s.delete_file("a")
    s.add_file("a", 99)
    expect(s.restore_user("u1"), 1)
    expect(s.get_file_size("a"), 99, "the admin's file stays")


@case("restoring without a backup deletes all of the user's files")
def no_backup(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_file_by("u1", "a", 10)
    expect(s.restore_user("u1"), 0)
    expect(s.get_file_size("a"), None)
    expect(s.add_file_by("u1", "b", 100), 0)
