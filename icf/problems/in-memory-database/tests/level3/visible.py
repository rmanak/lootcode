"""Level 3 — fields that expire (visible cases)."""
from icf_testkit import case, expect


@case("a field is alive up to, but not at, timestamp + ttl")
def ttl_boundary(Database):
    db = Database()
    db.set_with_ttl(1, "session", "token", "abc", 9)   # alive for [1, 10)
    expect(db.get(9, "session", "token"), "abc", "9 is inside the window")
    expect(db.get(10, "session", "token"), None, "10 is exactly the expiry")


@case("expired fields vanish from scan and scan_by_prefix")
def expired_not_scanned(Database):
    db = Database()
    db.set_with_ttl(1, "s", "token", "abc", 9)
    db.set(2, "s", "user", "ada")
    expect(db.scan(5, "s"), "token(abc), user(ada)")
    expect(db.scan(10, "s"), "user(ada)", "the token has expired by ts=10")
    expect(db.scan_by_prefix(11, "s", "to"), "")


@case("a plain set makes a previously expiring field permanent")
def set_clears_ttl(Database):
    db = Database()
    db.set_with_ttl(1, "s", "token", "abc", 5)
    db.set(2, "s", "token", "def")
    expect(db.get(999999, "s", "token"), "def", "the lifetime should be gone")


@case("set_with_ttl on an existing field restarts the countdown")
def ttl_restarts(Database):
    db = Database()
    db.set_with_ttl(1, "s", "token", "abc", 5)     # [1, 6)
    db.set_with_ttl(4, "s", "token", "def", 5)     # [4, 9)
    expect(db.get(6, "s", "token"), "def", "the second write pushed expiry to 9")
    expect(db.get(8, "s", "token"), "def")
    expect(db.get(9, "s", "token"), None)


@case("deleting an expired field reports False")
def delete_expired(Database):
    db = Database()
    db.set_with_ttl(1, "s", "token", "abc", 4)
    expect(db.delete(5, "s", "token"), False, "it expired at ts=5")
    expect(db.get(6, "s", "token"), None)


@case("compare_and_set fails on an expired field and keeps the ttl on success")
def cas_and_ttl(Database):
    db = Database()
    db.set_with_ttl(1, "s", "a", "one", 4)
    expect(db.compare_and_set(5, "s", "a", "one", "two"), False, "a is expired")

    db.set_with_ttl(6, "s", "b", "one", 10)        # [6, 16)
    expect(db.compare_and_set(7, "s", "b", "one", "two"), True)
    expect(db.get(15, "s", "b"), "two", "the lifetime is unchanged, so still alive")
    expect(db.get(16, "s", "b"), None, "and it still expires at 6 + 10")


@case("a field can be written again after it expires")
def rewrite_after_expiry(Database):
    db = Database()
    db.set_with_ttl(1, "s", "token", "abc", 2)
    expect(db.get(3, "s", "token"), None)
    db.set_with_ttl(4, "s", "token", "xyz", 2)
    expect(db.get(5, "s", "token"), "xyz")
    expect(db.scan(5, "s"), "token(xyz)")
