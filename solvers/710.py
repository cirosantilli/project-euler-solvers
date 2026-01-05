#!/usr/bin/env python
"""Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00710%20-%20One%20Million%20Members.py"""
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:35:15 2025

@author: Igor Van Loo
"""
"""
Project Euler Problem 710

"""
from functools import cache


@cache
def c1(n):
    if n <= 1:
        return 1
    return sum(c1(n - i) for i in range(1, n + 1)) - c1(n - 2)


@cache
def c2(n):
    if n <= 1:
        return 0
    return sum(c2(n - i) for i in range(1, n + 1)) + c1(n - 2)


@cache
def t(n):
    if n % 2 == 0:
        return sum(c2(i) for i in range(1, n // 2 + 1)) + c1(n // 2 - 1)
    return sum(c2(i) for i in range(1, n // 2 + 1))


def compute(N):
    c1 = [1, 1, 1] + [0] * N
    c2 = [0, 0, 1] + [0] * N
    sc1 = [1, 2, 3] + [0] * N
    sc2 = [0, 0, 1] + [0] * N
    t = [0, 0, 1] + [0] * N
    mod = 10**6
    n = 2
    while (t[n] != 0) or (n < 43):
        n += 1

        c2[n] = (sc2[n - 1] + c1[n - 2]) % mod
        c1[n] = (sc1[n - 1] - c1[n - 2]) % mod
        sc2[n] = (sc2[n - 1] + c2[n]) % mod
        sc1[n] = (sc1[n - 1] + c1[n]) % mod

        if n % 2 == 0:
            t[n] = (sc2[n // 2] + c1[n // 2 - 1]) % mod
        else:
            t[n] = (sc2[n // 2]) % mod

    return n


if __name__ == "__main__":
    assert t(6) == 4
    assert t(20) == 824
    assert t(42) == 1999923
    print(compute(2 * 10**6))
