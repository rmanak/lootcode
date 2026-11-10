"""Level 4 — backup and restore (hidden cases)."""
from icf_testkit import case, expect


@case("the backup is kept and can be restored again")
def restore_twice(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_file_by("u1", "a", 10)
    s.backup_user("u1")
    s.delete_file("a")
    expect(s.restore_user("u1"), 1)
    s.delete_file("a")
    expect(s.restore_user("u1"), 1)
    expect(s.get_file_size("a"), 10)


@case("a newer backup replaces the old one")
def newer_backup(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_file_by("u1", "a", 10)
    s.backup_user("u1")
    s.add_file_by("u1", "b", 10)
    expect(s.backup_user("u1"), 2)
    s.delete_file("a")
    s.delete_file("b")
    expect(s.restore_user("u1"), 2)


@case("an empty backup is still a backup")
def empty_backup(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    expect(s.backup_user("u1"), 0)
    s.add_file_by("u1", "a", 5)
    expect(s.restore_user("u1"), 0)
    expect(s.get_file_size("a"), None)


@case("restored files use the backed-up sizes and frees the user's capacity")
def sizes_and_capacity(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 30)
    s.add_file_by("u1", "a", 10)
    s.backup_user("u1")
    s.delete_file("a")
    s.add_file_by("u1", "a", 25)
    expect(s.restore_user("u1"), 1)
    expect(s.get_file_size("a"), 10)
    expect(s.add_file_by("u1", "b", 20), 0)


@case("the admin can be neither backed up nor restored")
def admin_refused(CloudStorage):
    s = CloudStorage()
    s.add_file("x", 1)
    expect(s.backup_user("admin"), None)
    expect(s.restore_user("admin"), None)
    expect(s.restore_user("ghost"), None)
    expect(s.get_file_size("x"), 1)


@case("merging discards the second user's backup, keeps the first's")
def merge_and_backup(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 50)
    s.add_user("u2", 50)
    s.add_file_by("u1", "a", 10)
    s.add_file_by("u2", "b", 10)
    s.backup_user("u1")
    s.backup_user("u2")
    s.merge_user("u1", "u2")
    s.add_user("u2", 50)
    expect(s.restore_user("u2"), 0, "the new u2 has no backup")
    expect(s.get_file_size("b"), 10, "b now belongs to u1 and was not touched")
    expect(s.restore_user("u1"), 1, "u1's backup has only a")
    expect(s.get_file_size("b"), None, "b was not in u1's backup")


@case("skipped files are restored alphabetically and the rest still count")
def alphabetical(CloudStorage):
    s = CloudStorage()
    s.add_user("u1", 100)
    s.add_user("u2", 100)
    for name in ("c", "a", "b"):
        s.add_file_by("u1", name, 10)
    s.backup_user("u1")
    for name in ("c", "a", "b"):
        s.delete_file(name)
    s.add_file_by("u2", "b", 1)
    expect(s.restore_user("u1"), 2)
    expect(s.get_n_largest("", 5), ["a(10)", "c(10)", "b(1)"])
