def myCalendarTwo(operations):
    bookings = []
    overlaps = []
    out = []
    for op in operations:
        _, s, e = op
        if any(s < oe and os < e for os, oe in overlaps):
            out.append(False)
        else:
            for bs, be in bookings:
                if s < be and bs < e:
                    overlaps.append((max(s, bs), min(e, be)))
            bookings.append((s, e))
            out.append(True)
    return out
