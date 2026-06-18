def findDuplicates(files):
    from collections import defaultdict
    groups = defaultdict(list)
    for path, content in files:
        groups[content].append(path)
    return [paths for paths in groups.values() if len(paths) > 1]
