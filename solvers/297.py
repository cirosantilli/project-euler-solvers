#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0297.cpp"""
fibonacci = []
fibo_sum = []


def zeckendorf(x):
    result = 0
    pos = len(fibonacci) - 1
    while x > 0:
        while fibonacci[pos] > x:
            pos -= 1
        x -= fibonacci[pos]
        result += 1
    return result


def search(x):
    pos = 0
    while fibonacci[pos + 1] <= x:
        pos += 1

    reduced = x - fibonacci[pos]
    if reduced == 0:
        return fibo_sum[pos]

    return fibo_sum[pos] + reduced + search(reduced)


def solve(limit: int) -> int:
    global fibonacci, fibo_sum
    fibonacci = [1, 2]
    fibo_sum = [1, 2]

    while fibonacci[-1] < limit:
        next_fibo = fibonacci[-1] + fibonacci[-2]
        fibonacci.append(next_fibo)

        next_sum = fibo_sum[-1] + fibo_sum[-2] + fibonacci[-3] - 1
        fibo_sum.append(next_sum)

    return search(limit - 1)


if __name__ == "__main__":
    assert solve(1000000) == 7894453
    print(solve(100000000000000000))
