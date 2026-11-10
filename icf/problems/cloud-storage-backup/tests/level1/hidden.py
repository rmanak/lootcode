"""Level 1 — files (hidden cases)."""
from icf_testkit import case, expect


@case("a deleted name is free again")
def name_reuse(CloudStorage):
    s = CloudStorage()
    s.add_file("x", 10)
    s.delete_file("x")
    expect(s.add_file("x", 3), True)
    expect(s.get_file_size("x"), 3)


@case("a copy is independent of its source")
def copy_independent(CloudStorage):
    s = CloudStorage()
    s.add_file("a", 9)
    s.copy_file("a", "b")
    expect(s.delete_file("a"), 9)
    expect(s.get_file_size("b"), 9)
    expect(s.copy_file("b", "a"), True, "copy back under the freed name")


@case("names are case-sensitive and may contain slashes and dots")
def names(CloudStorage):
    s = CloudStorage()
    expect(s.add_file("dir/File.TXT", 1), True)
    expect(s.add_file("dir/file.txt", 2), True)
    expect(s.get_file_size("dir/File.TXT"), 1)
    expect(s.get_file_size("dir/file.txt"), 2)


@case("a zero-byte file is a real file")
def zero_bytes(CloudStorage):
    s = CloudStorage()
    expect(s.add_file("empty", 0), True)
    expect(s.get_file_size("empty"), 0)
    expect(s.delete_file("empty"), 0)
    expect(s.add_file("empty", 0), True)


@case("many files stay consistent")
def many(CloudStorage):
    s = CloudStorage()
    for i in range(200):
        s.add_file(f"f{i}", i)
    for i in range(0, 200, 2):
        expect(s.delete_file(f"f{i}"), i)
    for i in range(200):
        expect(s.get_file_size(f"f{i}"), None if i % 2 == 0 else i)
