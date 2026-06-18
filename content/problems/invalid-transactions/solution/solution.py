def invalidTransactions(transactions):
    parsed = []
    for t in transactions:
        name, time, amount, city = t.split(",")
        parsed.append((name, int(time), int(amount), city))
    n = len(parsed)
    invalid = set()
    for i in range(n):
        name, time, amount, city = parsed[i]
        if amount > 1000:
            invalid.add(i)
            continue
        for j in range(n):
            if i != j:
                n2, t2, a2, c2 = parsed[j]
                if name == n2 and city != c2 and abs(time - t2) <= 60:
                    invalid.add(i)
                    break
    return [transactions[i] for i in sorted(invalid)]
