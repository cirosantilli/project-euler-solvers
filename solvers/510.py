#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0510.cpp"""


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def triangle(n):
    nn = n
    return nn * (nn + 1) // 2


def evaluate(limit):
    result = 0
    a = 1
    while a * a < limit:
        b = 1
        a2 = a * a
        while b <= a:
            b2 = b * b
            numerator = a2 * b2
            denominator = (a + b) * (a + b)
            c2 = numerator // denominator
            if c2 * denominator == numerator:
                if gcd(gcd(a2, b2), c2) == 1:
                    multiples = limit // a2
                    result += (a2 + b2 + c2) * triangle(multiples)
            b += 1
        a += 1
    return result


def main():
    assert evaluate(5) == 9
    assert evaluate(100) == 3072
    print(evaluate(1000000000))


if __name__ == "__main__":
    main()
