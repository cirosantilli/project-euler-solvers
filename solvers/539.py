#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0539.cpp'''
def brute_force_p(n):
    numbers = list(range(1, n + 1))
    left_to_right = True
    while len(numbers) > 1:
        next_numbers = []
        if left_to_right:
            idx = 1
        else:
            idx = len(numbers) % 2
        for i in range(idx, len(numbers), 2):
            next_numbers.append(numbers[i])
        left_to_right = not left_to_right
        numbers = next_numbers
    return numbers[0]


def brute_force_s(limit):
    total = 0
    for i in range(1, limit + 1):
        total += brute_force_p(i)
    return total


def fast_p(n):
    cache_size = 20
    if not hasattr(fast_p, "cache"):
        fast_p.cache = [0] * (cache_size + 1)
    cache = fast_p.cache

    if n <= cache_size:
        if cache[n] == 0:
            cache[n] = brute_force_p(n)
        return cache[n]

    result = fast_p(n // 4) * 4
    return result + (n & 2) - 2


def slow_s(limit, modulo=987654321):
    total = 0
    for i in range(1, limit + 1):
        current = fast_p(i)
        total += current
        if total > 10 * modulo:
            total %= modulo
    return total % modulo


def fast_s(_limit, _modulo=987654321):
    return 0


def main():
    assert fast_p(1) == 1
    assert fast_p(9) == 6
    assert fast_p(1000) == 510
    assert slow_s(1000) == 268271
    print(slow_s(1000000000000000000))


if __name__ == "__main__":
    main()
