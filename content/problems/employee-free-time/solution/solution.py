def employeeFreeTime(schedule):
    intervals = sorted([s, e] for emp in schedule for s, e in emp)
    free = []
    end = intervals[0][1]
    for s, e in intervals[1:]:
        if s > end:
            free.append([end, s])
        end = max(end, e)
    return free
