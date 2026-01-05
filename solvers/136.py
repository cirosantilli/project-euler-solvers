#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0136.cpp"""


def compute_flags(limit: int) -> tuple[bytearray, bytearray]:
    at_least_one = bytearray(limit)
    more_than_one = bytearray(limit)
    for a in range(1, limit):
        b = (a + 3) // 4
        while b < a:
            current = a * (4 * b - a)
            if current >= limit:
                break
            if at_least_one[current]:
                more_than_one[current] = 1
            else:
                at_least_one[current] = 1
            b += 1
    return at_least_one, more_than_one


def count_unique(limit: int) -> int:
    at_least_one, more_than_one = compute_flags(limit)
    count = 0
    for i in range(limit):
        if at_least_one[i] and not more_than_one[i]:
            count += 1
    return count


def main() -> None:
    small_at_least_one, small_more_than_one = compute_flags(100)
    assert small_at_least_one[20] and not small_more_than_one[20]
    assert count_unique(100) == 25

    print(count_unique(50000000))


if __name__ == "__main__":
    main()
