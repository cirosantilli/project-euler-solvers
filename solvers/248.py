#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0248.cpp"""
import bisect

factorial = 1
factors = {}
candidates = set()
results = []


def is_prime(p):
    bitmask_primes_2_to_31 = (
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
        return (bitmask_primes_2_to_31 & (1 << p)) != 0

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

    test_against_1 = [377687]
    test_against_2 = [31, 73]
    test_against_3 = [2, 7, 61]
    test_against_4 = [2, 13, 23, 1662803]
    test_against_7 = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]

    if p < 5329:
        test_against = test_against_1
    elif p < 9080191:
        test_against = test_against_2
    elif p < 4759123141:
        test_against = test_against_3
    elif p < 1122004669633:
        test_against = test_against_4
    else:
        test_against = test_against_7

    d = p - 1
    d >>= 1
    shift = 0
    while (d & 1) == 0:
        shift += 1
        d >>= 1

    for base in test_against:
        x = pow(base, d, p)
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


def find_candidates(number=1, last_prime=1):
    next_primes = [p for p in sorted(factors.keys()) if p > last_prime]
    if not next_primes:
        if is_prime(number + 1):
            candidates.add(number + 1)
        return

    base = next_primes[0]
    exponent = factors[base]
    for _ in range(exponent + 1):
        find_candidates(number, base)
        number *= base


def search(number=1, phi=1, largest_prime=1):
    candidates_sorted = search.candidates_sorted
    start = bisect.bisect_left(candidates_sorted, largest_prime)

    for current in candidates_sorted[start:]:
        next_number = number * current

        next_phi = phi * (current - 1)
        if current == largest_prime:
            next_phi += phi

        if next_phi > factorial:
            break
        if next_phi == factorial:
            results.append(next_number)
            break

        if factorial % next_phi == 0:
            search(next_number, next_phi, current)


def solve(thirteen: int, index: int) -> int:
    global factorial, factors
    candidates.clear()
    results.clear()
    factorial = 1
    for i in range(2, thirteen + 1):
        factorial *= i

    factors = {}
    reduce_value = factorial
    for i in range(2, thirteen + 1):
        while reduce_value % i == 0:
            factors[i] = factors.get(i, 0) + 1
            reduce_value //= i

    find_candidates()

    search.candidates_sorted = sorted(candidates)
    search()

    index -= 1
    results.sort()
    return results[index]


def main() -> None:
    assert solve(13, 1) == 6227180929
    print(solve(13, 150000))


if __name__ == "__main__":
    main()
