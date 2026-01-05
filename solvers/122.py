#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0122.cpp"""
from typing import List, Dict


Chain = List[int]


def search(chain: Chain, exponent: int, max_depth: int) -> bool:
    if len(chain) > max_depth:
        return False

    last = chain[-1]
    for i in range(len(chain)):
        sum_ = chain[len(chain) - 1 - i] + last
        if sum_ == exponent:
            return True

        chain.append(sum_)
        if search(chain, exponent, max_depth):
            return True
        chain.pop()

    return False


def find_chain(exponent: int, cache: Dict[int, Chain]) -> Chain:
    if exponent in cache:
        return cache[exponent][:]

    depth = 1
    while True:
        chain = [1]
        if search(chain, exponent, depth):
            cache[exponent] = chain[:]
            return chain
        depth += 1


def m(exponent: int, cache: Dict[int, Chain]) -> int:
    if exponent == 1:
        return 0
    chain = find_chain(exponent, cache)
    return len(chain)


def main() -> None:
    cache: Dict[int, Chain] = {}
    assert m(15, cache) == 5

    total = 0
    for exponent in range(2, 201):
        total += m(exponent, cache)
    print(total)


if __name__ == "__main__":
    main()
