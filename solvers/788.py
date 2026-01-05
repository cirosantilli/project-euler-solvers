#!/usr/bin/env python
"""Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00788%20-%20Dominating%20Numbers.py"""
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:36:37 2025

@author: Igor Van Loo
"""
"""
Project Euler Problem 788

D(N) = sum_{n = 1}^N sum_{m = n//2 + 1}^n c(n, m)

where c(n, m) = 9^(n - m + 1) nCm

"""


def factorial_mod(n, mod):
    factorial = [1] * (n + 1)
    for x in range(2, n + 1):
        factorial[x] = x * factorial[x - 1]
        factorial[x] %= mod
    return factorial


def D(N):
    mod = 10**9 + 7
    fac = factorial_mod(N, mod)

    def c(n, m):
        return (
            pow(9, n - m + 1, mod)
            * (fac[n] * pow(fac[n - m], -1, mod) * pow(fac[m], -1, mod))
        ) % mod

    return sum(c(n, m) for n in range(1, N + 1) for m in range(n // 2 + 1, n + 1)) % mod


def is_dominating(n):
    s = str(n)
    counts = [s.count(d) for d in set(s)]
    return max(counts) > len(s) / 2


if __name__ == "__main__":
    assert is_dominating(2022)
    assert not is_dominating(2021)
    assert D(4) == 603
    assert D(10) == 21893256
    print(D(2022))
