#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0130.cpp"""


def powmod(base: int, exponent: int, modulo: int) -> int:
    return pow(base, exponent, modulo)


def is_prime(p: int) -> bool:
    if p < 2:
        return False
    if p < 31:
        return p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)

    small_primes = (2, 3, 5, 7, 11, 13, 17)
    for prime in small_primes:
        if p % prime == 0:
            return False

    if p < 17 * 19:
        return True

    test_against1 = (377687, 0)
    test_against2 = (31, 73, 0)
    test_against3 = (2, 7, 61, 0)
    test_against4 = (2, 13, 23, 1662803, 0)
    test_against7 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022, 0)

    if p < 5329:
        test_against = test_against1
    elif p < 9080191:
        test_against = test_against2
    elif p < 4759123141:
        test_against = test_against3
    elif p < 1122004669633:
        test_against = test_against4
    else:
        test_against = test_against7

    d = p - 1
    shift = 0
    while d % 2 == 0:
        d //= 2
        shift += 1

    for base in test_against:
        if base == 0:
            break
        x = powmod(base, d, p)
        if x == 1 or x == p - 1:
            continue
        maybe_prime = False
        for _ in range(shift):
            x = (x * x) % p
            if x == 1:
                return False
            if x == p - 1:
                maybe_prime = True
                break
        if not maybe_prime:
            return False

    return True


def find_composites(target: int) -> list[int]:
    found: list[int] = []
    start = 91
    if start % 2 == 0:
        start += 1

    p = start
    while len(found) < target:
        if not is_prime(p) and powmod(10, p - 1, 9 * p) == 1:
            found.append(p)
        p += 2
    return found


def main() -> None:
    first_five = find_composites(5)
    assert first_five == [91, 259, 451, 481, 703]
    print(sum(find_composites(25)))


if __name__ == "__main__":
    main()
