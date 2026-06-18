def validIPAddress(IP):
    def is_v4(s):
        parts = s.split(".")
        if len(parts) != 4:
            return False
        for p in parts:
            if not p.isascii() or not p.isdigit():
                return False
            if len(p) > 1 and p[0] == '0':
                return False
            if not 0 <= int(p) <= 255:
                return False
        return True

    def is_v6(s):
        parts = s.split(":")
        if len(parts) != 8:
            return False
        hexd = set("0123456789abcdefABCDEF")
        for p in parts:
            if not 1 <= len(p) <= 4:
                return False
            if any(c not in hexd for c in p):
                return False
        return True

    if is_v4(IP):
        return "IPv4"
    if is_v6(IP):
        return "IPv6"
    return "Neither"
