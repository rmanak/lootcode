Given an absolute Unix-style file `path`, **return its simplified canonical path.**
Collapse `.` (current dir), `..` (parent dir), and redundant slashes; the result
starts with a single `/` and has no trailing slash (except the root `/`).

**Examples**
```
"/home/"          ->  "/home"
"/a/./b/../../c/" ->  "/c"
"/../"            ->  "/"
"/home//foo/"     ->  "/home/foo"
```

**Constraints:** `1 <= len(path) <= 3000`, valid absolute path.
