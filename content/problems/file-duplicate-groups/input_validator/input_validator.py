"""Input-constraint validator for problem 'file-duplicate-groups'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(files):
    if not isinstance(files, list):
        return False
    if len(files) < 0 or len(files) > 20000:
        return False
    seen_paths = set()
    for entry in files:
        if not isinstance(entry, list):
            return False
        if len(entry) != 2:
            return False
        path, content = entry
        if not isinstance(path, str) or not isinstance(content, str):
            return False
        if path in seen_paths:
            return False
        seen_paths.add(path)
    return True
