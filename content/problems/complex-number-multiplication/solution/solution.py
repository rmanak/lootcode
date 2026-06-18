def complexNumberMultiply(num1, num2):
    def parse(s):
        s = s[:-1]
        p = s.rfind('+')
        return int(s[:p]), int(s[p + 1:])
    a1, b1 = parse(num1)
    a2, b2 = parse(num2)
    real = a1 * a2 - b1 * b2
    imag = a1 * b2 + a2 * b1
    return "{}+{}i".format(real, imag)
