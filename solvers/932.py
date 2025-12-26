#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00932%20-%202025.py'''
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 22:52:33 2025

@author: Igor Van Loo
"""
'''
Project Euler Problem 932

Answer:
    72673459417881349
'''
import math

def compute(N):
    total = -1 #To account for (a, b) = (0, 1) solution
    for b in range(1, 10**(N//2)):
        n = len(str(b))
        v = 4*b*(1 - 10**n) + 10**(2*n)
        if v > 0:
            v = math.sqrt(v)
            if v == int(v):
                v = int(v)
                a = (10**n - 2*b + v)//2
                total += a*10**n + b
                    
                a = (10**n - 2*b - v)//2
                total += a*10**n + b
    return total

def is_2025_number(n):
    s = str(n)
    for i in range(1, len(s)):
        a = int(s[:i])
        b = int(s[i:])
        if a > 0 and b > 0 and (a + b) ** 2 == n:
            return True
    return False

if __name__ == "__main__":
    assert is_2025_number(2025)
    assert is_2025_number(3025)
    assert is_2025_number(81)
    # TODO extra assert
    #assert not is_2025_number(9801)
    assert compute(4) == 5131
    print(compute(16))
