#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0351.cpp'''
sieve = []


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


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def sum_phi_sliced(limit, segment_size=1000000):
    result = 1
    fill_sieve(limit)

    primes = [2]
    primes.reserve = None
    for i in range(3, limit + 1, 2):
        if is_prime(i):
            primes.append(i)

    phi = [0] * segment_size
    for start in range(2, limit + 1, segment_size):
        end = min(start + segment_size, limit + 1)
        size = end - start
        for i in range(size):
            phi[i] = start + i

        for p in primes:
            if p >= end:
                break
            first = (start + p - 1) // p * p
            if first < start:
                first += p
            for j in range(first, end, p):
                phi[j - start] = (phi[j - start] // p) * (p - 1)

        for i in range(size):
            result += phi[i]

    return result


def solve(limit=100000000):
    sum_phi = sum_phi_sliced(limit)
    return 6 * (limit * (limit + 1) // 2 - sum_phi)


def main():
    assert solve(5) == 30
    assert solve(10) == 138
    assert solve(1000) == 1177848
    print(solve())


if __name__ == "__main__":
    main()
