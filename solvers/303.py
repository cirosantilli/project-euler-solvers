#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0303.cpp"""
FAST999 = True


def next_permutation(seq):
    i = len(seq) - 2
    while i >= 0 and seq[i] >= seq[i + 1]:
        i -= 1
    if i < 0:
        return False
    j = len(seq) - 1
    while seq[j] <= seq[i]:
        j -= 1
    seq[i], seq[j] = seq[j], seq[i]
    seq[i + 1 :] = reversed(seq[i + 1 :])
    return True


def solve(limit: int) -> int:
    total = 0

    open_numbers = list(range(1, limit + 1))

    if limit >= 9999:
        total += 11112222222222222222 // 9999
        del open_numbers[9999 - 1]

    if FAST999:
        for factor in range(10, 0, -1):
            current = factor * 999
            if current > limit:
                continue

            digits = list("111222222222222")
            while True:
                multiple = int("".join(digits))
                if factor % 5 == 0:
                    multiple *= 10

                if multiple % current == 0:
                    total += multiple // current
                    del open_numbers[current - 1]
                    break

                if not next_permutation(digits):
                    break

    zero_one_two = [1, 2]

    while open_numbers:
        next_open = []
        for current in open_numbers:
            last_must_be_zero = current % 5 == 0
            found = False
            for multiple in zero_one_two:
                candidate = multiple * 10 if last_must_be_zero else multiple
                if candidate % current == 0:
                    total += candidate // current
                    found = True
                    break
            if not found:
                next_open.append(current)

        open_numbers = next_open
        if open_numbers:
            longer = []
            for multiple in zero_one_two:
                longer.append(multiple * 10)
                longer.append(multiple * 10 + 1)
                longer.append(multiple * 10 + 2)
            zero_one_two = longer

    return total


if __name__ == "__main__":
    assert solve(100) == 11363107
    print(solve(10000))
