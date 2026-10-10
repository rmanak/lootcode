"""Level 4 — backup and restore (visible cases)."""
from icf_testkit import case, expect


@case("backup counts the records that hold at least one live field")
def backup_counts_records(Database):
    db = Database()
    db.set(1, "a", "x", "1")
    db.set(2, "b", "y", "2")
    db.set_with_ttl(3, "c", "z", "3", 2)      # expires at 5
    expect(db.backup(4), 3, "all three records have a live field at ts=4")
    expect(db.backup(6), 2, "record 'c' has nothing left alive at ts=6")


@case("restore rolls writes back to the chosen snapshot")
def restore_discards_later_writes(Database):
    db = Database()
    db.set(1, "cfg", "region", "eu-west")
    db.backup(10)
    db.set(20, "cfg", "region", "us-east")
    db.restore(30, 15)
    expect(db.get(31, "cfg", "region"), "eu-west")


@case("restore removes records created after the snapshot was taken")
def restore_removes_new_records(Database):
    db = Database()
    db.set(1, "cfg", "a", "1")
    db.backup(10)
    db.set(20, "later", "b", "2")
    db.restore(30, 10)
    expect(db.get(31, "later", "b"), None)
    expect(db.scan(32, "later"), "")
    expect(db.get(33, "cfg", "a"), "1", "the snapshotted record is still here")


@case("a restored lifetime resumes from the restore timestamp")
def restore_resumes_ttl(Database):
    db = Database()
    db.set_with_ttl(2, "cfg", "lease", "node-a", 100)   # alive for [2, 102)
    db.backup(10)                                       # 92 ms left
    db.restore(200, 15)
    expect(db.get(291, "cfg", "lease"), "node-a", "92 ms from 200 runs to 292")
    expect(db.get(292, "cfg", "lease"), None)


@case("restore picks the most recent backup at or before at_timestamp")
def restore_picks_latest_eligible(Database):
    db = Database()
    db.set(1, "k", "f", "first")
    db.backup(10)
    db.set(11, "k", "f", "second")
    db.backup(20)
    db.set(21, "k", "f", "third")
    db.backup(30)
    db.restore(40, 25)
    expect(db.get(41, "k", "f"), "second", "the snapshot at 20 is the right one")


@case("backups survive being restored, and can be restored out of order")
def backups_are_reusable(Database):
    db = Database()
    db.set(1, "k", "f", "one")
    db.backup(10)
    db.set(11, "k", "f", "two")
    db.backup(20)

    db.restore(30, 20)
    expect(db.get(31, "k", "f"), "two")
    db.restore(40, 10)
    expect(db.get(41, "k", "f"), "one", "an older snapshot can be restored after")
    db.restore(50, 20)
    expect(db.get(51, "k", "f"), "two", "and the newer one is still available")
