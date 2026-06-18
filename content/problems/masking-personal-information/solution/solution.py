def maskPII(S):
    if '@' in S:
        name, domain = S.split('@')
        name = name.lower()
        return name[0] + "*****" + name[-1] + "@" + domain.lower()
    digits = [c for c in S if c.isdigit()]
    local = "".join(digits[-10:])
    country = digits[:-10]
    local_masked = "***-***-" + local[-4:]
    if country:
        return "+" + "*" * len(country) + "-" + local_masked
    return local_masked
