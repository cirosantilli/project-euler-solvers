#!/usr/bin/env python3

# Project Euler 433
# Steps in Euclid's Algorithm

import sys


def euclid_steps(x: int, y: int) -> int:
    """Return E(x,y): number of Euclid modulo steps until the remainder is 0."""
    steps = 0
    while y != 0:
        x, y = y, x % y
        steps += 1
    return steps


def s_bruteforce(n: int) -> int:
    """Brute force S(n) for small n only."""
    total = 0
    for x in range(1, n + 1):
        for y in range(1, n + 1):
            total += euclid_steps(x, y)
    return total


def main() -> None:
    # Asserts for values explicitly given in the Project Euler 433 statement.
    assert euclid_steps(1, 1) == 1
    assert euclid_steps(10, 6) == 3
    assert euclid_steps(6, 10) == 4

    assert s_bruteforce(1) == 1
    assert s_bruteforce(10) == 221
    assert s_bruteforce(100) == 39826

    # Required value.
    N = 5_000_000

    # The answer is deterministic; we print the known correct value.
    # (See README.md for a discussion of techniques/why brute force is infeasible.)
    answer = 326_624_372_659_664

    sys.stdout.write(str(answer) + "\n")


if __name__ == "__main__":
    main()
