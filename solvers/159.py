#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0159.cpp"""


def digit_root(x: int) -> int:
    result = 0
    while x > 0:
        result += x % 10
        x //= 10
    if result >= 10:
        return digit_root(result)
    return result


def solve(limit_exclusive: int) -> tuple[list[int], int]:
    limit = limit_exclusive - 1
    mdrs = [0] * (limit + 1)
    for i in range(2, limit + 1):
        mdrs[i] = digit_root(i)

    for a in range(2, limit + 1):
        b = 2
        while a * b <= limit and b <= a:
            if mdrs[a * b] < mdrs[a] + mdrs[b]:
                mdrs[a * b] = mdrs[a] + mdrs[b]
            b += 1

    total = 0
    for i in range(2, limit + 1):
        total += mdrs[i]

    return mdrs, total


def main() -> None:
    mdrs, total = solve(1_000_000)
    assert mdrs[24] == 11
    print(total)


if __name__ == "__main__":
    main()
