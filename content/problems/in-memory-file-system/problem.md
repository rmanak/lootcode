Implement an in-memory file system and replay `operations`, returning the list of
results. Operations are `["mkdir", path]` (create a directory, making parents as
needed; returns `null`), `["addContentToFile", path, content]` (create/append;
returns `null`), `["readContentFromFile", path]` (returns the file's content), and
`["ls", path]`: if `path` is a file, return `[filename]`; if a directory, return its
entry names (files and subdirectories) **sorted** alphabetically.

## Constraints
- `1 <= len(operations) <= 300`
- paths are absolute, using `/` as separator

## Examples
Input: `operations = [["mkdir","/a/b"],["addContentToFile","/a/b/f","hi"],["ls","/a/b"],["readContentFromFile","/a/b/f"]]`
Output: `[null,null,["f"],"hi"]`
Explanation: The file `f` is created under `/a/b` with content `hi`.

Input: `operations = [["ls","/"]]`
Output: `[[]]`
Explanation: The empty root lists nothing.
