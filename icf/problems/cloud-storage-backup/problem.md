### Instructions

Your task is to implement a simplified version of a cloud storage system. A
service like this keeps people's files on a shared server: users upload files,
copy and delete them, look for their biggest files when space runs low, and
take backups so that a mistake can be undone. All operations that should be
supported are described in the levels below.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `CloudStorage`. Plan your design according to the level
specifications below:

- **Level 1:** The cloud storage system should support adding, copying,
  deleting and measuring files.
- **Level 2:** The cloud storage system should support finding the largest
  files whose names start with a given prefix.
- **Level 3:** The cloud storage system should support users with storage
  capacities, and merging two users' accounts into one.
- **Level 4:** The cloud storage system should support backing up a user's
  files and restoring them later.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so everything you built earlier must keep working.

### Notes

- All files live in one shared namespace: a file name, such as
  `"/dir1/dir2/file.txt"`, identifies exactly one file no matter who owns it.
  Names are case-sensitive, and the slashes are ordinary characters — there
  are no real directories to create.
- File sizes are non-negative integers, in bytes.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `CloudStorage()` holds no files.
