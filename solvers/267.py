#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0267.cpp'''
import functools
import math


def get_min_heads(tosses, billion, step=0.0001):
    result = tosses
    ratio = 0.0
    while ratio < 1.0:
        won = 1.0 + 2.0 * ratio
        lost = 1.0 - ratio

        heads = result
        while heads > 0:
            total = pow(won, heads) * pow(lost, tosses - heads)
            if total < billion:
                heads += 1
                break
            heads -= 1

        if result > heads:
            result = heads
        ratio += step

    return result


def probability(min_heads, max_tosses):
    @functools.lru_cache(maxsize=None)
    def helper(tosses, heads):
        if heads >= min_heads:
            return 1.0
        if max_tosses - tosses < min_heads - heads:
            return 0.0

        return 0.5 * helper(tosses + 1, heads + 1) + 0.5 * helper(tosses + 1, heads)

    return helper(0, 0)


def solve(tosses: int, money: float) -> float:
    min_heads = get_min_heads(tosses, money)
    return probability(min_heads, tosses)


def main():
    print(f"{solve(1000, 1000000000.0):.12f}")


if __name__ == "__main__":
    main()
