#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0273.cpp"""
SEED = (1, 0)
primes = []


def is_4n1_prime(p):
    if p % 4 != 1:
        return False
    i = 3
    while i * i <= p:
        if p % i == 0:
            return False
        i += 2
    return p > 1


def process_prime(prime):
    b = 1
    while b * b < prime:
        a = 1
        while a < b:
            if a * a + b * b == prime:
                return (a, b)
            a += 1
        b += 1
    return (0, 0)


def search(solutions=None, index=0):
    if solutions is None:
        solutions = [SEED]

    if index == len(primes):
        total = 0
        for s in solutions:
            if s != SEED:
                total += s[0]
        return total

    current = primes[index]
    next_solutions = []
    for s in solutions:
        x = s[0] * current[0] + s[1] * current[1]
        y = abs(s[0] * current[1] - s[1] * current[0])
        if x > y:
            x, y = y, x
        next_solutions.append((x, y))

        if s == SEED:
            continue

        x = abs(s[0] * current[0] - s[1] * current[1])
        y = s[0] * current[1] + s[1] * current[0]
        if x > y:
            x, y = y, x
        next_solutions.append((x, y))

    without = search(solutions, index + 1)
    with_current = search(next_solutions, index + 1)
    return with_current + without


def sum_of_a_values(limit: int) -> int:
    primes.clear()
    for i in range(5, limit + 1, 4):
        if is_4n1_prime(i):
            primes.append(process_prime(i))
    return search()


def brute_s(n: int) -> int:
    total = 0
    for a in range(int(n**0.5) + 1):
        for b in range(a, int(n**0.5) + 1):
            if a * a + b * b == n:
                total += a
    return total


def main():
    assert brute_s(65) == 5
    print(sum_of_a_values(150))


if __name__ == "__main__":
    main()
