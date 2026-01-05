#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0341.cpp"""
import math


def build_golomb_to_index(max_index):
    golomb = [0, 1]
    i = 2
    while i <= max_index:
        current = 1 + golomb[i - golomb[golomb[i - 1]]]
        golomb.append(current)
        i += 1
    return golomb


def golomb_at(n):
    golomb = build_golomb_to_index(n)
    return golomb[n]


def solve(limit=1000000):
    cubic_limit = limit * limit * limit

    golomb = [0, 1]
    products = 1
    i = 2
    while products < cubic_limit:
        current = 1 + golomb[i - golomb[golomb[i - 1]]]
        golomb.append(current)
        products += current * i
        i += 1

    total = 0
    last_sums = 0
    sums = 1
    last_products = 0
    products = 1

    index = 1
    for i in range(1, limit):
        n = i * i * i
        while products < n:
            index += 1
            last_sums = sums
            sums += golomb[index]
            last_products = products
            products += golomb[index] * index

        from_value = last_products
        to_value = products
        ratio = (n - from_value) / float(to_value - from_value)

        low = last_sums
        high = sums

        offset = math.ceil((high - low) * ratio)
        result = int(offset) + low
        total += result

    return total


def main():
    assert golomb_at(1000) == 86
    assert golomb_at(1000000) == 6137
    assert solve(1000) == 153506976
    print(solve())


if __name__ == "__main__":
    main()
