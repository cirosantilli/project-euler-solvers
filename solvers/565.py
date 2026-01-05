#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0565.cpp"""
import bisect


def mulmod(a, b, modulo):
    return (a * b) % modulo


def powmod(base, exponent, modulo):
    return pow(base, exponent, modulo)


def is_prime(p):
    bitmask_primes2to31 = (
        (1 << 2)
        | (1 << 3)
        | (1 << 5)
        | (1 << 7)
        | (1 << 11)
        | (1 << 13)
        | (1 << 17)
        | (1 << 19)
        | (1 << 23)
        | (1 << 29)
    )
    if p < 31:
        return (bitmask_primes2to31 & (1 << p)) != 0

    if (
        p % 2 == 0
        or p % 3 == 0
        or p % 5 == 0
        or p % 7 == 0
        or p % 11 == 0
        or p % 13 == 0
        or p % 17 == 0
    ):
        return False

    if p < 17 * 19:
        return True

    stop = 0
    test_against1 = [377687, stop]
    test_against2 = [31, 73, stop]
    test_against3 = [2, 7, 61, stop]
    test_against4 = [2, 13, 23, 1662803, stop]
    test_against7 = [2, 325, 9375, 28178, 450775, 9780504, 1795265022, stop]

    test_against = test_against7
    if p < 5329:
        test_against = test_against1
    elif p < 9080191:
        test_against = test_against2
    elif p < 4759123141:
        test_against = test_against3
    elif p < 1122004669633:
        test_against = test_against4

    d = p - 1
    d >>= 1
    shift = 0
    while (d & 1) == 0:
        shift += 1
        d >>= 1

    for base in test_against:
        if base == stop:
            break
        x = powmod(base, d, p)
        if x == 1 or x == p - 1:
            continue

        maybe_prime = False
        for _ in range(shift):
            x = mulmod(x, x, p)
            if x == 1:
                return False
            if x == p - 1:
                maybe_prime = True
                break

        if not maybe_prime:
            return False

    return True


def search(limit, multiple):
    found = []
    if limit == 100000000000:
        found = []

    p = 2
    while p * p <= limit:
        if not is_prime(p):
            p += 1
            continue

        power = p * p
        while power <= limit:
            sigma = (power * p - 1) // (p - 1)
            if sigma % multiple == 0:
                i = 1
                while i * power <= limit:
                    if i % p != 0:
                        found.append(i * power)
                    i += 1

            if limit // power < p:
                break
            power *= p

        p += 1

    result = 0
    sorted_size = 0

    p = multiple - 1
    while p <= limit:
        if not is_prime(p):
            p += multiple
            continue

        if sorted_size == 0 and p * p > limit:
            found.sort()
            sorted_size = len(found)

        i = 1
        while i * p <= limit:
            if i % p != 0:
                current = i * p
                if i < multiple - 1:
                    result += current
                elif sorted_size > 0:
                    idx = bisect.bisect_left(found, current, 0, sorted_size)
                    if idx == sorted_size or found[idx] != current:
                        result += current
                else:
                    found.append(current)
            i += 1

        p += multiple

    found.sort()
    last = None
    for value in found:
        if value != last:
            result += value
            last = value

    return result


def main():
    assert search(20, 7) == 49
    assert search(1000000, 2017) == 150850429
    assert search(1000000000, 2017) == 249652238344557
    print(search(100000000000, 2017))


if __name__ == "__main__":
    main()
