"""Level 4 — compression (visible cases)."""
from icf_testkit import case, expect


@case("compress_file replaces a file with a .COMPRESSED file of half the size")
def compress_halves(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 1000)
    expect(storage.add_file_by("user1", "/dir/file.mp4", 500), 500)
    expect(storage.compress_file("user1", "/dir/file.mp4"), 750)
    expect(storage.get_file_size("/dir/file.mp4"), None)
    expect(storage.get_file_size("/dir/file.mp4.COMPRESSED"), 250)


@case("decompress_file takes the compressed name and restores the original file")
def decompress_restores(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 1000)
    storage.add_file_by("user1", "/dir/file.mp4", 500)
    storage.compress_file("user1", "/dir/file.mp4")
    expect(storage.decompress_file("user1", "/dir/file.mp4.COMPRESSED"), 500)
    expect(storage.get_file_size("/dir/file.mp4"), 500)
    expect(storage.get_file_size("/dir/file.mp4.COMPRESSED"), None)


@case("compression is refused for an unknown user, a missing file, or another user's file")
def compress_refused(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 1000)
    storage.add_user("user2", 5000)
    storage.add_file_by("user1", "/dir/file.mp4", 500)
    expect(storage.compress_file("user2", "/dir/file.mp4"), None, "owned by user1")
    expect(storage.compress_file("user3", "/dir/file.mp4"), None, "no such user")
    expect(storage.compress_file("user1", "/folder/non_existing_file"), None, "no such file")
    expect(storage.get_file_size("/dir/file.mp4"), 500, "nothing changed")
    expect(storage.compress_file("user1", "/dir/file.mp4"), 750)


@case("decompression is refused when the restored file would not fit")
def decompress_does_not_fit(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 1000)
    storage.add_file_by("user1", "/a", 800)
    expect(storage.compress_file("user1", "/a"), 600)
    expect(storage.add_file_by("user1", "/b", 500), 100)
    expect(storage.decompress_file("user1", "/a.COMPRESSED"), None, "it needs 400 more bytes")
    expect(storage.get_file_size("/a.COMPRESSED"), 400, "the compressed file is untouched")
    expect(storage.update_capacity("user1", 1300), 0)
    expect(storage.decompress_file("user1", "/a.COMPRESSED"), 0)


@case("decompression is refused while a file with the original name exists")
def decompress_name_taken(CloudStorage):
    storage = CloudStorage()
    storage.add_user("user1", 1000)
    storage.add_file_by("user1", "/a", 100)
    expect(storage.compress_file("user1", "/a"), 950)
    expect(storage.add_file_by("user1", "/a", 10), 940, "the name is free while compressed")
    expect(storage.decompress_file("user1", "/a.COMPRESSED"), None)
    expect(storage.get_file_size("/a"), 10)
    expect(storage.get_file_size("/a.COMPRESSED"), 50)
