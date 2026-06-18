def canAvoidFlood(rains):
    import bisect
    full = {}        # lake -> day it was last filled
    dry_days = []    # sorted indices of available dry days
    for i, r in enumerate(rains):
        if r == 0:
            bisect.insort(dry_days, i)
        else:
            if r in full:
                pos = bisect.bisect_right(dry_days, full[r])
                if pos == len(dry_days):
                    return False
                dry_days.pop(pos)
            full[r] = i
    return True
