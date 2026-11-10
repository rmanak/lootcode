"""Level 1 — files (visible cases)."""
from icf_testkit import case, expect


@case("a file is added once and its size can be read back")
def add_and_size(CloudStorage):
    s = CloudStorage()
    expect(s.add_file("a.txt", 100), True)
    expect(s.add_file("a.txt", 5), False, "the name is taken")
    expect(s.get_file_size("a.txt"), 100, "the refused add changed nothing")
    expect(s.get_file_size("b.txt"), None)


@case("delete returns the size of the removed file")
def delete_returns_size(CloudStorage):
    s = CloudStorage()
    s.add_file("a.txt", 40)
    expect(s.delete_file("a.txt"), 40)
    expect(s.get_file_size("a.txt"), None)
    expect(s.delete_file("a.txt"), None, "already gone")


@case("copy creates a second file of the same size")
def copy(CloudStorage):
    s = CloudStorage()
    s.add_file("a", 7)
    expect(s.copy_file("a", "b"), True)
    expect(s.get_file_size("b"), 7)
    expect(s.get_file_size("a"), 7, "the original stays")


@case("copy fails for a missing source or a taken destination")
def copy_fails(CloudStorage):
    s = CloudStorage()
    s.add_file("a", 1)
    s.add_file("b", 2)
    expect(s.copy_file("zzz", "c"), False)
    expect(s.copy_file("a", "b"), False)
    expect(s.get_file_size("b"), 2, "the destination is untouched")
    expect(s.copy_file("a", "a"), False, "a file cannot be copied onto itself")
