#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0523.cpp'''
import itertools
from decimal import Decimal, getcontext


def evaluate(size):
    data = list(range(1, size + 1))

    moves = 0
    permutations = 0
    for perm in itertools.permutations(data):
        current = list(perm)
        permutations += 1
        pos = 1
        while pos < size:
            if current[pos] < current[pos - 1]:
                current[: pos + 1] = current[pos : pos + 1] + current[:pos]
                moves += 1
                pos = 1
            else:
                pos += 1

    print(f"E({size})={moves / float(permutations)} ={moves}/{permutations}")
    return moves / float(permutations)


def solve(limit=30):
    getcontext().prec = 50
    result = Decimal(0)
    for i in range(1, limit + 1):
        numerator = (Decimal(2) ** (i - 1)) - 1
        result += numerator / Decimal(i)
    return result


def main():
    assert solve(4).quantize(Decimal(\"0.001\")) == Decimal(\"3.250\")
    assert solve(10).quantize(Decimal(\"0.001\")) == Decimal(\"115.725\")
    print(f\"{solve().quantize(Decimal('0.01')):.2f}\")


if __name__ == "__main__":
    main()
