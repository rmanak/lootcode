"""Level 2 — finding files (visible cases)."""
from icf_testkit import case, expect


@case("matching files are listed from the largest to the smallest")
def by_size(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/dir/small.txt", 5)
    storage.add_file("/dir/big.txt", 50)
    storage.add_file("/dir/medium.txt", 20)
    expect(storage.find_file("/dir/", ".txt"),
           ["/dir/big.txt(50)", "/dir/medium.txt(20)", "/dir/small.txt(5)"])


@case("files of the same size are listed in lexicographic order of their names")
def ties_by_name(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/dir/c.txt", 9)
    storage.add_file("/dir/a.txt", 9)
    storage.add_file("/dir/b.txt", 9)
    expect(storage.find_file("/dir/", ".txt"),
           ["/dir/a.txt(9)", "/dir/b.txt(9)", "/dir/c.txt(9)"])


@case("a file must match both the prefix and the suffix")
def both_sides(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/dir/file1.txt", 5)
    storage.add_file("/dir/file2.mov", 20)
    storage.add_file("/other/file3.txt", 9)
    expect(storage.find_file("/dir/", ".txt"), ["/dir/file1.txt(5)"])
    expect(storage.find_file("/dir/", ".mov"), ["/dir/file2.mov(20)"])


@case("find_file returns an empty list when nothing matches")
def no_match(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/dir/file.txt", 5)
    expect(storage.find_file("/dir", ".mp3"), [])
    expect(storage.find_file("/file", ".txt"), [], "names must start with the prefix")
    expect(storage.find_file("/dir", ".txt"), ["/dir/file.txt(5)"])
