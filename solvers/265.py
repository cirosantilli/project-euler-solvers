#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0265.cpp"""
bits = 5


def search(history, sequence):
    mask = (1 << bits) - 1
    all_bits = (1 << (1 << bits)) - 1
    if history == all_bits:
        sequence >>= bits - 1
        return sequence

    next_value = (sequence << 1) & mask
    zero = next_value
    one = next_value + 1

    result = 0
    if (history & (1 << zero)) == 0:
        result += search(history | (1 << zero), sequence << 1)
    if (history & (1 << one)) == 0:
        result += search(history | (1 << one), (sequence << 1) | 1)

    return result


def solve(num_bits: int) -> int:
    global bits
    bits = num_bits
    return search(1, 0)


def main():
    assert solve(3) == 52
    print(solve(5))


if __name__ == "__main__":
    main()
