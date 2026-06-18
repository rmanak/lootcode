A file system is encoded in a single string `s`. Lines are separated by `\n`; the
number of leading `\t` (tab) characters on a line is its depth. A name containing a
`.` is a file; otherwise it is a directory. **Return the length of the longest
absolute path to a file** (joining names with `/`), or `0` if there is no file.

**Examples**
```
s = "dir\n\tsubdir1\n\tsubdir2\n\t\tfile.ext"  ->  20   ("dir/subdir2/file.ext")
s = "dir\n\tsubdir1\n\t\tfile1.ext\n\t\tsubsubdir1\n\tsubdir2\n\t\tsubsubdir2\n\t\t\tfile2.ext"
    ->  32   ("dir/subdir2/subsubdir2/file2.ext")
```

**Constraints:** a file name has at least one `.`; directory names have none.
