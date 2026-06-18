def ledgerBalance(transactions):
    bal = {}
    for frm, to, amt in transactions:
        bal[frm] = bal.get(frm, 0) - amt
        bal[to] = bal.get(to, 0) + amt
    return bal
