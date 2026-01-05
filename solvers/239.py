#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0239.cpp"""


def factorial(n: int) -> float:
    result = 1.0
    while n > 1:
        result *= n
        n -= 1
    return result


def choose(n: int, k: int) -> float:
    return factorial(n) / (factorial(n - k) * factorial(k))


def derangements(move: int, dont_care: int) -> float:
    if move < 1:
        return factorial(dont_care)

    move -= 1
    result = dont_care * derangements(move, dont_care)
    if move > 0:
        result += move * derangements(move - 1, dont_care + 1)
    return result


def solve(moved: int) -> float:
    disks = 100
    primes = 25

    if moved > primes:
        return

    unchanged = primes - moved

    result = derangements(moved, disks - primes)
    result *= choose(primes, unchanged)
    result /= factorial(disks)

    return result


def main() -> None:
    print(f"{solve(22):.12f}")


if __name__ == "__main__":
    main()
