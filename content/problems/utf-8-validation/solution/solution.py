def validUtf8(data):
    n_bytes = 0
    for num in data:
        b = num & 0xFF
        if n_bytes == 0:
            if b >> 7 == 0:
                n_bytes = 0
            elif b >> 5 == 0b110:
                n_bytes = 1
            elif b >> 4 == 0b1110:
                n_bytes = 2
            elif b >> 3 == 0b11110:
                n_bytes = 3
            else:
                return False
        else:
            if b >> 6 != 0b10:
                return False
            n_bytes -= 1
    return n_bytes == 0
