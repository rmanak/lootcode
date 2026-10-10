"""Level 1 — files (visible cases)."""
from icf_testkit import case, expect


@case("add_file stores a new file, and get_file_size reads its size back")
def add_and_read(CloudStorage):
    storage = CloudStorage()
    expect(storage.add_file("/dir1/dir2/file.txt", 10), True)
    expect(storage.get_file_size("/dir1/dir2/file.txt"), 10)


@case("a file name can only be added once, and the first file is kept")
def add_duplicate(CloudStorage):
    storage = CloudStorage()
    expect(storage.add_file("/a.txt", 10), True)
    expect(storage.add_file("/a.txt", 15), False, "the name is taken")
    expect(storage.get_file_size("/a.txt"), 10, "the original size is kept")


@case("copy_file creates a second file of the same size and keeps the original")
def copy_creates(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/dir1/dir2/file.txt", 10)
    expect(storage.copy_file("/dir1/dir2/file.txt", "/dir1/file.txt"), True)
    expect(storage.get_file_size("/dir1/file.txt"), 10)
    expect(storage.get_file_size("/dir1/dir2/file.txt"), 10, "the original is still there")


@case("copying a file that does not exist is refused")
def copy_missing(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a.txt", 3)
    expect(storage.copy_file("/not-existing.file", "/b.txt"), False)
    expect(storage.get_file_size("/b.txt"), None, "nothing was created")
    expect(storage.copy_file("/a.txt", "/b.txt"), True)


@case("copying onto a file that already exists is refused")
def copy_onto_existing(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a.txt", 3)
    storage.add_file("/b.txt", 7)
    expect(storage.copy_file("/a.txt", "/b.txt"), False)
    expect(storage.get_file_size("/b.txt"), 7, "the existing file is not overwritten")


@case("a directory is not a file, so it cannot be copied")
def copy_directory(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/dir1/dir2/file.txt", 10)
    expect(storage.copy_file("/dir1/dir2", "/backup"), False)
    expect(storage.copy_file("/dir1", "/backup"), False)
    expect(storage.get_file_size("/backup"), None)
    expect(storage.copy_file("/dir1/dir2/file.txt", "/backup"), True)


@case("get_file_size returns None for a file that does not exist")
def size_missing(CloudStorage):
    storage = CloudStorage()
    storage.add_file("/a.txt", 4)
    expect(storage.get_file_size("/not-existing.file"), None)
    expect(storage.get_file_size("/a.txt"), 4)
