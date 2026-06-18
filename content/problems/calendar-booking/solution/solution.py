def calendarBooking(operations):
    booked, out = [], []
    for op in operations:
        _, s, e = op
        ok = all(not (s < be and bs < e) for bs, be in booked)
        if ok:
            booked.append((s, e))
            out.append(True)
        else:
            out.append(False)
    return out
