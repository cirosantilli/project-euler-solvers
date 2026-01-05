#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0155.cpp"""
from fractions import Fraction


def solve(limit: int) -> int:
    circuits: list[set[Fraction]] = [set() for _ in range(limit + 1)]
    circuits[1].add(Fraction(1, 1))

    for size_c in range(2, limit + 1):
        current = set()
        for size_a in range(1, size_c // 2 + 1):
            size_b = size_c - size_a
            for circuit_a in circuits[size_a]:
                for circuit_b in circuits[size_b]:
                    current.add(circuit_a + circuit_b)
                    parallel = 1 / (1 / circuit_a + 1 / circuit_b)
                    current.add(parallel)
        circuits[size_c] = current

    all_values: set[Fraction] = set()
    for i in range(1, limit + 1):
        all_values.update(circuits[i])

    return len(all_values)


def main() -> None:
    assert solve(1) == 1
    assert solve(2) == 3
    assert solve(3) == 7
    print(solve(18))


if __name__ == "__main__":
    main()
