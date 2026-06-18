def snapshotArray(length, operations):
    import bisect
    records = [[(-1, 0)] for _ in range(length)]
    snap_id = 0
    out = []
    for op in operations:
        if op[0] == "set":
            _, index, val = op
            if records[index][-1][0] == snap_id:
                records[index][-1] = (snap_id, val)
            else:
                records[index].append((snap_id, val))
            out.append(None)
        elif op[0] == "snap":
            out.append(snap_id)
            snap_id += 1
        else:
            _, index, sid = op
            arr = records[index]
            i = bisect.bisect_right(arr, (sid, float('inf'))) - 1
            out.append(arr[i][1])
    return out
