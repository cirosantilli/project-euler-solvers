#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0156.cpp"""
base = 10


def count_single(digit: int, value: int) -> int:
    if value == 0 and digit == 0:
        return 1

    result = 0
    while value > 0:
        if value % base == digit:
            result += 1
        value //= base
    return result


def count(digit: int, value: int) -> int:
    if value < base:
        return 0 if value < digit else 1

    shift = 1
    multiplier = 0
    while shift * base <= value:
        shift *= base
        multiplier += 1
    multiplier *= shift // base

    first = value // shift
    remainder = value % shift

    result = first * multiplier
    result += count(digit, remainder)

    if digit == first:
        result += remainder + 1
    if digit < first and digit > 0:
        result += shift

    return result


def find_all(digit: int, start: int, end: int) -> int:
    center = (start + end) // 2
    if start == center:
        current = count(digit, start)
        return start if current == start else 0

    result = 0
    count_from = count(digit, start)

    while count_from == start and start < end:
        result += start
        start += 1
        count_from += count_single(digit, start)
    if start >= end + 1:
        return result

    center = (start + end) // 2

    count_center = count(digit, center)
    count_to = count(digit, end)

    if count_center >= start and center >= count_from and center > start:
        result += find_all(digit, start, center)
    if count_to >= center and end >= count_center and center < end:
        result += find_all(digit, center, end)

    return result


def solve(digits: list[int], limit: int) -> dict[int, int]:
    results = {}
    for digit in digits:
        results[digit] = find_all(digit, 0, limit)
    return results


def main() -> None:
    global base
    base = 10
    limit = 1000000000000
    results = solve(list(range(1, 10)), limit)
    assert results[1] == 22786974071
    print(sum(results.values()))


if __name__ == "__main__":
    main()
