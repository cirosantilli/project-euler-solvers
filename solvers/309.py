#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0309.cpp"""


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def solve(limit: int) -> int:
    sides = [[] for _ in range(limit)]

    m = 2
    while m * m < limit:
        n = (m & 1) + 1
        while n < m:
            if gcd(m, n) != 1:
                n += 2
                continue

            a = m * m - n * n
            b = 2 * m * n
            c = m * m + n * n

            k = 1
            while k * c < limit:
                sides[k * a].append(k * b)
                sides[k * b].append(k * a)
                k += 1

            n += 2
        m += 1

    count = 0
    for current in sides:
        for left in range(len(current)):
            for right in range(left + 1, len(current)):
                x = current[left]
                y = current[right]
                if (x * y) % (x + y) == 0:
                    count += 1

    return count


if __name__ == "__main__":
    assert solve(200) == 5
    print(solve(1000000))
