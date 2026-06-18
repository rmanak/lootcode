def minRemovals(s):
    open_unmatched = 0
    removals = 0
    for ch in s:
        if ch == '(':
            open_unmatched += 1
        elif ch == ')':
            if open_unmatched > 0:
                open_unmatched -= 1
            else:
                removals += 1
    return removals + open_unmatched
