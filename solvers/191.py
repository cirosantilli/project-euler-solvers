#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0191.cpp"""
cache = [0] * (80 * 2 * 3)


def count(days: int, absent: int = 0, late: int = 0) -> int:
    if absent == 3:
        return 0
    if late > 1:
        return 0
    if days == 0:
        return 1

    hash_value = days * 2 * 3 + absent * 2 + late
    if cache[hash_value] != 0:
        return cache[hash_value]

    result = 0
    result += count(days - 1, 0, late)
    result += count(days - 1, absent + 1, late)
    result += count(days - 1, 0, late + 1)

    cache[hash_value] = result
    return result


def main() -> None:
    assert count(4) == 43
    print(count(30))


if __name__ == "__main__":
    main()
