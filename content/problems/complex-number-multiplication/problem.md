You are given two strings `num1` and `num2`, each a complex number written in the form
`"a+bi"`, where `a` and `b` are integers and `i` is the imaginary unit with `i^2 = -1`.
Return their product, also formatted as `"a+bi"`.

**Examples**
```
num1 = "1+1i",  num2 = "1+1i"    ->  "0+2i"     ((1+i)(1+i) = 2i)
num1 = "1+-1i", num2 = "1+-1i"   ->  "0+-2i"    ((1-i)(1-i) = -2i)
```

**Constraints:** the integers `a` and `b` are in `[-100, 100]`; the input has no spaces.
