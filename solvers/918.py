#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00918%20-%20Recursive%20Sequence%20Summation.py'''
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:50:16 2025

@author: Igor Van Loo
"""
'''
Project Euler Problem 918

S(N) = sum_{n = 1}^N a_n

a_{2n} = 2a_n
a_{2n + 1} = a_n - 3a_{n + 1}

Simple expansion of S(N) gives us

S(N) = 4 - a_{N//2} if N is even
S(n) = 4 - 3a_{N//2 + 1} if N is odd

Answer:
    -6999033352333308
'''

from functools import cache

@cache
def a(n):
    if n == 1:
        return 1
    if n % 2 == 0:
        return 2*a(n//2)
    return a(n//2) - 3*a(n//2 + 1)

def S(N):
    if N % 2 == 0:
        return 4 - a(N//2)
    return 4 - 3*a(N//2 + 1)

if __name__ == "__main__":
    assert [a(i) for i in range(1, 11)] == [1, 2, -5, 4, 17, -10, -17, 8, -47, 34]
    assert S(10) == -13
    print(S(10**12))
