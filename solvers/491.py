#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0491.cpp"""
import itertools


def brute_force(max_digit):
    digits = list("10012233445566778899")
    digits = digits[: max_digit * 2 + 2]

    result = 0
    for perm in set(itertools.permutations(digits)):
        if int("".join(perm)) % 11 == 0:
            result += 1
    return result


def next_number_with_same_bits(x):
    smallest = x & -x
    ripple = x + smallest
    ones = ripple ^ x
    return ((ones >> 2) // smallest) | ripple


def fast(max_digit):
    result = 0
    digit_sum = 2 * (max_digit + 1) * max_digit // 2
    num_digits = 2 * (max_digit + 1)

    factorial = 1
    for i in range(1, max_digit + 2):
        factorial *= i

    permutations_repeated = [0] * (max_digit + 1)
    for i in range(0, max_digit + 1):
        permutations_repeated[i] = factorial >> i

    min_bitmask = (1 << (max_digit + 1)) - 1
    max_bitmask = min_bitmask << (max_digit + 1)

    bitmask = min_bitmask
    while bitmask <= max_bitmask:
        reduce_mask = bitmask
        ok = True
        while reduce_mask > 0:
            if (reduce_mask & 3) == 2:
                ok = False
                break
            reduce_mask >>= 2
        if ok:
            sum_odd = 0
            repeated = 0
            for pos in range(num_digits):
                if bitmask & (1 << pos):
                    sum_odd += pos // 2
                    if pos & 1:
                        repeated += 1

            if (digit_sum - 2 * sum_odd) % 11 == 0:
                result += (
                    permutations_repeated[repeated] * permutations_repeated[repeated]
                )

        if bitmask == max_bitmask:
            break
        bitmask = next_number_with_same_bits(bitmask)

    return result * max_digit // (max_digit + 1)


def main():
    print(fast(9))


if __name__ == "__main__":
    main()
