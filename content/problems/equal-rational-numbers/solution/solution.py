def isRationalEqual(S, T):
    from fractions import Fraction

    def parse(s):
        rep = ''
        if '(' in s:
            base, rep = s.split('(')
            rep = rep[:-1]
        else:
            base = s
        if '.' in base:
            intpart, frac = base.split('.')
        else:
            intpart, frac = base, ''
        intpart = intpart or '0'
        val = Fraction(int(intpart))
        if frac:
            val += Fraction(int(frac), 10 ** len(frac))
        if rep:
            denom = (10 ** len(rep) - 1) * (10 ** len(frac))
            val += Fraction(int(rep), denom)
        return val

    return parse(S) == parse(T)
