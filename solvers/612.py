#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0612.cpp'''
MODULO = 1000267129


def fingerprint(x):
    result = 0
    while x > 0:
        digit = x % 10
        result |= 1 << digit
        x //= 10
    return result


def brute_force(limit):
    result = 0
    for q in range(1, limit):
        mask_q = fingerprint(q)
        for p in range(1, q):
            mask_p = fingerprint(p)
            if (mask_q & mask_p) != 0:
                result += 1
                if result == MODULO:
                    result = 0
    return result


def slow(limit):
    result = 0
    num_counters = 1 << 10
    mask_count = [0] * num_counters

    for q in range(1, limit):
        mask_q = fingerprint(q)
        for i in range(1, num_counters):
            if i & mask_q:
                result += mask_count[i]
                if result >= MODULO:
                    result %= MODULO

        mask_count[mask_q] += 1
        if mask_count[mask_q] == MODULO:
            mask_count[mask_q] = 0

    return result


def main():
    assert slow(100) == 1539
    print(slow(1000000))


if __name__ == "__main__":
    main()
