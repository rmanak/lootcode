"""Level 4 — backup and restore (hidden cases)."""
from icf_testkit import case, expect


@case("a snapshot omits fields that had already expired")
def backup_omits_expired(Database):
    db = Database()
    db.set_with_ttl(1, "k", "gone", "x", 3)     # expires at 4
    db.set(2, "k", "kept", "y")
    expect(db.backup(5), 1)
    db.set(6, "k", "extra", "z")
    db.restore(7, 5)
    expect(db.scan(8, "k"), "kept(y)", "only the live field was snapshotted")


@case("a field expiring exactly at the backup timestamp is not saved")
def backup_boundary(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "v", 9)        # alive for [1, 10)
    expect(db.backup(10), 0, "nothing is alive at ts=10")
    db.set(11, "k", "other", "w")
    db.restore(12, 10)
    expect(db.scan(13, "k"), "", "the restored snapshot was empty")


@case("permanent fields come back permanent")
def permanent_survives_restore(Database):
    db = Database()
    db.set(1, "k", "f", "v")
    db.backup(2)
    db.set(3, "k", "f", "changed")
    db.restore(4, 2)
    expect(db.get(10 ** 9, "k", "f"), "v")


@case("restoring the same snapshot twice gives the same state both times")
def restore_is_repeatable(Database):
    db = Database()
    db.set_with_ttl(1, "k", "f", "v", 50)       # 49 left at the backup
    db.backup(2)
    db.restore(100, 2)
    expect(db.get(148, "k", "f"), "v")
    expect(db.get(149, "k", "f"), None, "expired at 100 + 49")
    db.restore(1000, 2)
    expect(db.get(1048, "k", "f"), "v", "the same 49 ms, counted again")
    expect(db.get(1049, "k", "f"), None)


@case("a record whose fields all expired is not restored at all")
def fully_expired_record_dropped(Database):
    db = Database()
    db.set_with_ttl(1, "ghost", "f", "v", 2)    # expires at 3
    db.set(1, "solid", "f", "v")
    expect(db.backup(4), 1)
    db.restore(5, 4)
    expect(db.scan(6, "ghost"), "")
    expect(db.get(7, "ghost", "f"), None)
    expect(db.scan(8, "solid"), "f(v)")


@case("everything else keeps working on restored data")
def level_one_and_two_after_restore(Database):
    db = Database()
    db.set(1, "k", "b", "2")
    db.set(2, "k", "a", "1")
    db.backup(3)
    db.set(4, "k", "c", "3")
    db.restore(5, 3)
    expect(db.scan(6, "k"), "a(1), b(2)")
    expect(db.scan_by_prefix(7, "k", "b"), "b(2)")
    expect(db.compare_and_set(8, "k", "a", "1", "9"), True)
    expect(db.delete(9, "k", "b"), True)
    expect(db.scan(10, "k"), "a(9)")


@case("a backup taken after a restore snapshots the restored state")
def backup_after_restore(Database):
    db = Database()
    db.set(1, "k", "f", "original")
    db.backup(2)
    db.set(3, "k", "f", "edited")
    db.restore(4, 2)
    expect(db.backup(5), 1)
    db.set(6, "k", "f", "edited again")
    db.restore(7, 5)
    expect(db.get(8, "k", "f"), "original",
           "the ts=5 snapshot holds what the restore had put back")


@case("a long mixed sequence of backups, restores and lifetimes stays consistent")
def long_mixed_scenario(Database):
    db = Database()
    db.set(1, "users", "alice", "admin")
    db.set(2, "users", "bob", "reader")
    db.set_with_ttl(3, "cache", "page1", "html", 20)    # [3, 23)
    expect(db.backup(4), 2)                             # users + cache

    db.set(5, "users", "carol", "reader")
    db.delete(6, "users", "bob")
    expect(db.backup(7), 2)

    expect(db.scan(8, "users"), "alice(admin), carol(reader)")
    db.restore(9, 4)
    expect(db.scan(10, "users"), "alice(admin), bob(reader)",
           "carol is gone and bob is back")
    expect(db.get(11, "cache", "page1"), "html",
           "19 ms were left at ts=4, so it lives until 28")
    expect(db.get(28, "cache", "page1"), None)

    db.restore(30, 7)
    expect(db.scan(31, "users"), "alice(admin), carol(reader)")
    expect(db.get(32, "cache", "page1"), "html", "16 ms left at ts=7 → until 46")
    expect(db.get(46, "cache", "page1"), None)
    expect(db.backup(47), 1)
