#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0237.cpp"""
LEFT_BORDER = "1##2"
RIGHT_BORDER = "####"

borders = set()
neighbors = set()


def fill() -> None:
    entries = [
        ("1234", "1234"),
        ("1432", "1432"),
        ("3214", "3214"),
        ("1432", "1##2"),
        ("3214", "1##2"),
        ("1##2", "1234"),
        ("1234", "12##"),
        ("1234", "##12"),
        ("12##", "1432"),
        ("##12", "3214"),
        ("1##2", "#12#"),
        ("#12#", "1##2"),
        ("12##", "1##2"),
        ("1##2", "##12"),
        ("1##2", "12##"),
        ("##12", "1##2"),
        ("1234", RIGHT_BORDER),
        ("1##2", RIGHT_BORDER),
    ]
    for left, right in entries:
        neighbors.add((left, right))
        borders.add(left)


def search(left: str, right: str, length: int, modulo: int, cache: dict) -> int:
    if length == 1:
        return 1 if (left, right) in neighbors else 0

    key = (left, right, length)
    if key in cache:
        return cache[key]

    result = 0
    for nxt in borders:
        pow2 = 1
        while pow2 < length // 2:
            pow2 *= 2

        left_half = search(left, nxt, pow2, modulo, cache)
        right_half = search(nxt, right, length - pow2, modulo, cache)
        result += (left_half * right_half) % modulo

    result %= modulo
    cache[key] = result
    return result


def solve(limit: int) -> int:
    fill()
    modulo = 100000000
    cache = {}
    return search(LEFT_BORDER, RIGHT_BORDER, limit, modulo, cache)


def main() -> None:
    assert solve(10) == 2329
    print(solve(1000000000000))


if __name__ == "__main__":
    main()
