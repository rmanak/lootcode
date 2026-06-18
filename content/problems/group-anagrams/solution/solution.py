def groupAnagrams(strs):
    from collections import defaultdict
    groups = defaultdict(list)
    for w in strs:
        groups[''.join(sorted(w))].append(w)
    res = [sorted(v) for v in groups.values()]
    res.sort()
    return res
