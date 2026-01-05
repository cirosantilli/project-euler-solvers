#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0134.cpp"""


def tens(x: int) -> int:
    result = 1
    while result <= x:
        result *= 10
    return result


def extended_gcd(a: int, b: int):
    s, last_s = 0, 1
    t, last_t = 1, 0
    r, last_r = b, a
    while r != 0:
        quotient = last_r // r
        last_r, r = r, last_r - quotient * r
        last_s, s = s, last_s - quotient * s
        last_t, t = t, last_t - quotient * t
    return last_s, last_t, last_r


def chinese_remainder(small_prime: int, large_prime: int) -> int:
    modulo1 = large_prime
    modulo2 = tens(small_prime)
    x, _y, _gcd = extended_gcd(modulo1, modulo2)
    result = small_prime * x * modulo1
    product = modulo1 * modulo2
    result %= product
    if result < 0:
        result += product
    return result


def solve(limit: int) -> int:
    total = 0
    primes = [2]
    i = 3
    while True:
        is_prime = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_prime = False
                break
        if not is_prime:
            i += 2
            continue

        last_prime = primes[-1]
        primes.append(i)
        if last_prime >= 5:
            total += chinese_remainder(last_prime, i)

        if i > limit:
            break
        i += 2
    return total


def main() -> None:
    assert chinese_remainder(19, 23) == 1219
    print(solve(1000000))


if __name__ == "__main__":
    main()
