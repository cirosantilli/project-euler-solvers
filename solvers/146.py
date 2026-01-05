#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0146.cpp"""


def mulmod(a: int, b: int, modulo: int) -> int:
    return (a * b) % modulo


def powmod(base: int, exponent: int, modulo: int) -> int:
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = mulmod(result, base, modulo)
        base = mulmod(base, base, modulo)
        exponent >>= 1
    return result


def is_prime(p: int, fast_check: bool = True) -> bool:
    if fast_check:
        small_mask = (
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
            return (small_mask & (1 << p)) != 0
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
            x = mulmod(x, x, p)
            if x == 1:
                return False
            if x == p - 1:
                maybe_prime = True
                break
        if not maybe_prime:
            return False

    return True


def solve(limit: int) -> tuple[int, list[int]]:
    primes = [2]
    i = 3
    while i < 500:
        is_p = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_p = False
                break
        if is_p:
            primes.append(i)
        i += 2

    good = [1, 3, 7, 9, 13, 27]
    parity = good[0] % 2
    same_parity = all(x % 2 == parity for x in good)
    if not same_parity:
        return 0, []

    bad = []
    for i in range(parity, good[-1], 2):
        if i not in good:
            bad.append(i)

    increment = 2
    start = 1 - parity
    if len(bad) >= 2 and bad[0] == 5 and bad[1] > 9:
        increment = 10

    total = 0
    values: list[int] = []
    for n in range(start, limit, increment):
        square = n * n

        if square % 3 == 0 or square % 7 == 0 or square % 13 == 0:
            continue

        ok = True
        for p in primes:
            for check in good:
                current = square + check
                if current != p and current % p == 0:
                    ok = False
                    break
            if not ok:
                break

        if ok:
            for x in good:
                if ok and not is_prime(square + x, False):
                    ok = False
            for x in bad:
                if ok and is_prime(square + x, True):
                    ok = False

        if ok:
            total += n
            values.append(n)

    return total, values


def main() -> None:
    total_small, values_small = solve(1_000_000)
    assert values_small and values_small[0] == 10
    assert total_small == 1242490
    total, _values = solve(150_000_000)
    print(total)


if __name__ == "__main__":
    main()
