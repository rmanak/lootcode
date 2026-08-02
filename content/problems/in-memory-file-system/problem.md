Design an in-memory file system that supports creating directories, appending to
files, reading files, and listing a path.

Implement the `FileSystem` class:

- `FileSystem()` initializes the object with an empty root directory `/`.
- `String[] ls(String path)` — if `path` is a **file path**, returns a list
  containing just that file's name; if `path` is a **directory path**, returns the
  names of the files and subdirectories directly inside it, **sorted**
  lexicographically. Returns an empty list for an empty directory.
- `void mkdir(String path)` makes the directory `path`, creating any missing
  intermediate directories along the way.
- `void addContentToFile(String filePath, String content)` appends `content` to the
  file at `filePath`, creating the file (and any missing directories) if it does
  not exist.
- `String readContentFromFile(String filePath)` returns the whole content of the
  file at `filePath`.

All paths are absolute and use `/` as the separator; the root is `"/"`.

**Example 1:**

```
Input
["FileSystem", "mkdir", "addContentToFile", "ls", "readContentFromFile"]
[[], ["/a/b"], ["/a/b/f", "hi"], ["/a/b"], ["/a/b/f"]]

Output
[null, null, null, ["f"], "hi"]
```

Explanation: `/a/b` is created, then the file `f` is written under it with content
`"hi"`.

**Example 2:**

```
Input
["FileSystem", "ls"]
[[], ["/"]]

Output
[null, []]
```

Explanation: listing the empty root returns nothing.

**Constraints:**

- `1 <= path.length, filePath.length <= 100`
- Paths are absolute, contain no trailing `/` except for the root, and use only
  lowercase letters, digits, and `/`.
- `1 <= content.length <= 50`
- At most `300` calls will be made across all methods.
