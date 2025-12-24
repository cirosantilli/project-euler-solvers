#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0501.cpp'''
import bisect
import math

primes = []


def count_primes(n):
    if primes and primes[-1] > n:
        return bisect.bisect_right(primes, n)

    v = int(math.isqrt(n))
    higher = [0] * (v + 2)
    lower = [0] * (v + 2)
    used = [False] * (v + 2)

    result = n - 1

    for p in range(2, v + 1):
        lower[p] = p - 1
        higher[p] = n // p - 1

    for p in range(2, v + 1):
        if lower[p] == lower[p - 1]:
            continue

        if not primes or p > primes[-1]:
            primes.append(p)

        temp = lower[p - 1]
        result -= higher[p] - temp

        p_square = p * p
        end = min(v, n // p_square)
        j = 1 + (p & 1)

        for i in range(p + j, end + 2, j):
            if used[i]:
                continue
            d = i * p
            if d <= v:
                higher[i] -= higher[d] - temp
            else:
                higher[i] -= lower[n // d] - temp

        for i in range(v, p_square - 1, -1):
            lower[i] -= lower[i // p] - temp

        for i in range(p_square, end + 1, p * j):
            used[i] = True

    return result


def fast(n):
    count_primes(n)

    count_abc = 0
    for index_a, a in enumerate(primes):
        if a * a * a > n:
            break
        for index_b in range(index_a + 1, len(primes)):
            b = primes[index_b]
            max_c = n // (a * b)
            if max_c <= b:
                break
            high = count_primes(max_c)
            low = index_b + 1
            count_abc += high - low

    count_a3b = 0
    for a in primes:
        max_b = n // (a * a * a)
        if max_b <= 1:
            break
        num_b = count_primes(max_b)
        if max_b >= a:
            num_b -= 1
        count_a3b += num_b

    count_a7 = 0
    for a in primes:
        if a ** 7 > n:
            break
        count_a7 += 1

    return count_abc + count_a3b + count_a7


def main():
    assert fast(100) == 10
    assert fast(1000) == 180
    assert fast(1000000) == 224427
    print(fast(1000000000000))


if __name__ == "__main__":
    main()
