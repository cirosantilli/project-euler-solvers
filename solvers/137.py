#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0137.cpp"""


def mulmod(a: int, b: int, modulo: int) -> int:
    return (a * b) % modulo


def nugget(n: int, modulo: int) -> int:
    n *= 2
    fibo = [[1, 1], [1, 0]]
    result = [[1, 0], [0, 1]]

    while n > 0:
        if n & 1:
            t00 = mulmod(result[0][0], fibo[0][0], modulo) + mulmod(
                result[0][1], fibo[1][0], modulo
            )
            t01 = mulmod(result[0][0], fibo[0][1], modulo) + mulmod(
                result[0][1], fibo[1][1], modulo
            )
            t10 = mulmod(result[1][0], fibo[0][0], modulo) + mulmod(
                result[1][1], fibo[1][0], modulo
            )
            t11 = mulmod(result[1][0], fibo[0][1], modulo) + mulmod(
                result[1][1], fibo[1][1], modulo
            )

            if t00 >= modulo:
                t00 -= modulo
            if t01 >= modulo:
                t01 -= modulo
            if t10 >= modulo:
                t10 -= modulo
            if t11 >= modulo:
                t11 -= modulo

            result = [[t00, t01], [t10, t11]]

        t00 = mulmod(fibo[0][0], fibo[0][0], modulo) + mulmod(
            fibo[0][1], fibo[1][0], modulo
        )
        t01 = mulmod(fibo[0][0], fibo[0][1], modulo) + mulmod(
            fibo[0][1], fibo[1][1], modulo
        )
        t10 = mulmod(fibo[1][0], fibo[0][0], modulo) + mulmod(
            fibo[1][1], fibo[1][0], modulo
        )
        t11 = mulmod(fibo[1][0], fibo[0][1], modulo) + mulmod(
            fibo[1][1], fibo[1][1], modulo
        )

        if t00 >= modulo:
            t00 -= modulo
        if t01 >= modulo:
            t01 -= modulo
        if t10 >= modulo:
            t10 -= modulo
        if t11 >= modulo:
            t11 -= modulo

        fibo = [[t00, t01], [t10, t11]]
        n >>= 1

    return (result[0][0] * result[0][1]) % modulo


def main() -> None:
    modulo = 10000000000000
    assert nugget(10, modulo) == 74049690
    print(nugget(15, modulo))


if __name__ == "__main__":
    main()
