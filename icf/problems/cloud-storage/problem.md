### Instructions

Your task is to implement a simplified version of a cloud storage system. A
cloud storage service keeps people's files on remote servers so they can reach
them from anywhere: users upload files, make copies of them, search for them,
and pay for a fixed amount of space. The system you are building maps each
file to its metainformation — its name, its size, and later who owns it. The
system is kept entirely in memory: you do not need to work with the real file
system, and the contents of the files are never stored, only the information
about them.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

You are not required to provide the most efficient implementation. Any code
that passes the tests is sufficient.

### Requirements

Implement the class `CloudStorage`. Plan your design according to the level
specifications below:

- **Level 1:** The cloud storage system should support adding new files,
  retrieving their sizes, and copying files.
- **Level 2:** The cloud storage system should support finding files by
  matching the prefixes and suffixes of their names.
- **Level 3:** The cloud storage system should support adding users with
  various storage capacity limits.
- **Level 4:** The cloud storage system should support compressing and
  decompressing files.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### The data model

A **file** has a name and a size in bytes. The name is the file's full path,
such as `"/dir1/dir2/file.txt"`, and it is unique across the whole storage.
The parts of a path that come before a `/` are **directories**: in that
example, `"/dir1"` and `"/dir1/dir2"` are directories. Directories are not
stored on their own. They exist only as parts of file names, and no operation
creates or removes one.

It is guaranteed that the given queries will never call operations that result
in collisions between file and directory names: while `"/dir1/dir2/file.txt"`
exists, no file will be named `"/dir1/dir2"` or `"/dir1"`.

Apart from that, names are plain, case-sensitive strings, so `"/Dir/a.txt"` and
`"/dir/a.txt"` are two different files.

### Notes

- There are no timestamps in this task: operations take effect in the order in
  which they are called.
- File names and user ids are non-empty strings. File sizes are positive
  integers and capacities are non-negative integers, both measured in bytes.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `CloudStorage()` has no files and no users.
