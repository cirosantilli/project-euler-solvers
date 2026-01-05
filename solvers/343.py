#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0343.cpp"""
import math

sieve = []
prime_limit = 0
small_primes = []


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def is_small_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = (size >> 1) + 1
    sieve = [True] * half
    if half > 0:
        sieve[0] = False

    i = 1
    while 2 * i * i < half:
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = False
                current += step
        i += 1


def mulmod(a, b, modulo):
    return (a * b) % modulo


def powmod(base, exponent, modulo):
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = mulmod(result, base, modulo)
        base = mulmod(base, base, modulo)
        exponent >>= 1
    return result


def is_prime(p):
    if p < prime_limit:
        return is_small_prime(p)

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


def get_fermat_factors(n, max_iterations):
    if n % 2 == 0:
        return (2, n // 2)

    x = int(math.isqrt(n))
    if x * x == n:
        return (x, x)

    while max_iterations > 0:
        max_iterations -= 1
        x += 1
        y2 = x * x - n
        mod16 = y2 % 16
        if mod16 in (0, 1, 4, 9):
            y = int(math.isqrt(y2))
            if y * y == y2:
                return (x - y, x + y)

    return (1, n)


def get_max_factor(x, min_result=0):
    if is_prime(x):
        return x

    result = 1
    reduce_value = x
    for factor in small_primes:
        if factor * factor > reduce_value:
            break

        found_factor = False
        while reduce_value % factor == 0:
            result = max(result, factor)
            reduce_value //= factor

            if reduce_value < min_result:
                return result

            found_factor = True

        if found_factor:
            if is_prime(reduce_value):
                break

            fermat = get_fermat_factors(reduce_value, 10)
            if fermat[0] > 1:
                return max(get_max_factor(fermat[0]), get_max_factor(fermat[1]))

    return max(reduce_value, result)


def f_simple(k):
    x = 1
    y = k
    while y != 1:
        x += 1
        y -= 1
        g = gcd(x, y)
        x //= g
        y //= g
    return x


def solve(limit=2000000):
    global prime_limit, small_primes

    prime_limit = limit + 100
    fill_sieve(prime_limit)

    small_primes = [2]
    for i in range(3, prime_limit + 1, 2):
        if is_prime(i):
            small_primes.append(i)

    total = 0
    for i in range(1, limit + 1):
        a = i + 1
        b = i * i - i + 1

        factor2 = get_max_factor(b)
        factor1 = 1
        if factor2 < a:
            factor1 = get_max_factor(a, factor2)

        factor = max(factor1, factor2)
        total += factor - 1

    return total


def main():
    assert f_simple(1) == 1
    assert f_simple(2) == 2
    assert f_simple(3) == 1
    assert f_simple(20) == 6
    assert solve(100) == 118937
    print(solve())


if __name__ == "__main__":
    main()
