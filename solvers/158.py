#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0158.cpp"""


def choose(n: int, k: int) -> int:
    result = 1
    for inv_k in range(1, k + 1):
        result *= n
        result //= inv_k
        n -= 1
    return result


def count(n: int, alphabet: int) -> int:
    if n > alphabet:
        return 0

    result = 0
    for i in range(1, n):
        result += choose(n, i) - 1

    return result * choose(alphabet, n)


def solve(alphabet: int, size: int) -> int:
    best = 0
    for i in range(2, size + 1):
        current = count(i, alphabet)
        if best < current:
            best = current

    return best


def main() -> None:
    assert count(3, 26) == 10400
    print(solve(26, 26))


if __name__ == "__main__":
    main()
