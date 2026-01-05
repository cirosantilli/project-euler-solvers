#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0516.cpp"""
import bisect


def is_prime(x):
    if x % 2 == 0 or x % 3 == 0 or x % 5 == 0:
        return x == 2 or x == 3 or x == 5

    delta = [6, 4, 2, 4, 2, 4, 6, 2]
    i = 7
    pos = 1
    while i * i <= x:
        if x % i == 0:
            return False
        i += delta[pos]
        pos = (pos + 1) & 7
    return x > 1


def solve(limit=1000000000000):
    hamming = []
    primes = []

    two = 1
    while two <= limit:
        three = 1
        while two * three <= limit:
            five = 1
            while two * three * five <= limit:
                current = two * three * five
                hamming.append(current)
                if current > 5 and is_prime(current + 1):
                    primes.append(current + 1)
                five *= 5
            three *= 3
        two *= 2

    hamming.sort()
    primes.sort()

    todo = [(1, 1)]
    total = 0
    while todo:
        number, largest_prime = todo.pop()

        for x in hamming:
            next_value = x * number
            if next_value > limit:
                break
            total += next_value

        idx = bisect.bisect_right(primes, largest_prime)
        for prime in primes[idx:]:
            next_value = prime * number
            if next_value > limit:
                break
            todo.append((next_value, prime))

    total &= 0xFFFFFFFF
    return total


def main():
    assert solve(100) == 3728
    print(solve())


if __name__ == "__main__":
    main()
