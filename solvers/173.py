#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0173.cpp"""


def solve(limit: int) -> int:
    count = 0
    outer = 3
    while True:
        total = 0
        inner = outer
        while inner >= 3:
            ring = 4 * (inner - 1)
            if total + ring > limit:
                break
            total += ring
            count += 1
            inner -= 2

        if total == 0:
            break
        outer += 1
    return count


def main() -> None:
    assert solve(100) == 41
    print(solve(1000000))


if __name__ == "__main__":
    main()
