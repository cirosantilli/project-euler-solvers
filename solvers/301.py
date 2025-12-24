#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0301.cpp'''

def evaluate(n1, n2, n3):
    return n1 ^ n2 ^ n3


def solve(exponent: int) -> int:
    lost = 0
    n = 1 << exponent
    while n > 0:
        if evaluate(n, 2 * n, 3 * n) == 0:
            lost += 1
        n -= 1
    return lost


def main():
    assert solve(0) == 1
    assert solve(1) == 1
    print(solve(30))


if __name__ == "__main__":
    main()
