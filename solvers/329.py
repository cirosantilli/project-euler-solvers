#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0329.cpp"""


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def probability(square, depth, max_depth, limit, is_prime, sequence, cache):
    chance = 1
    if is_prime[square] ^ (sequence[depth] == "N"):
        chance = 2

    if depth == max_depth:
        return chance

    idx = square * max_depth + depth
    cached = cache[idx]
    if cached:
        return cached

    left = square - 1
    if left < 1:
        left = 2
    right = square + 1
    if right > limit:
        right = limit - 1

    result = chance * (
        probability(left, depth + 1, max_depth, limit, is_prime, sequence, cache)
        + probability(right, depth + 1, max_depth, limit, is_prime, sequence, cache)
    )
    cache[idx] = result
    return result


def solve(limit=500, max_depth=15):
    sequence = " PPPPNNPPPNPPNPN"

    is_prime = [True] * (limit + 1)
    if limit >= 1:
        is_prime[1] = False
    i = 2
    while i * i <= limit:
        if is_prime[i]:
            j = i * i
            while j <= limit:
                is_prime[j] = False
                j += i
        i += 1

    cache = [0] * ((max_depth + 1) * (limit + 1))

    total = 0
    for i in range(1, limit + 1):
        total += probability(i, 1, max_depth, limit, is_prime, sequence, cache)

    denominator = limit
    for _ in range(1, max_depth):
        denominator *= 3 * 2
    denominator *= 3

    divide = gcd(total, denominator)
    return f"{total // divide}/{denominator // divide}"


def main():
    print(solve())


if __name__ == "__main__":
    main()
