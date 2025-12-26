#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00820%20-%20nth%20digit%20reciprocals.py'''
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 10:42:24 2023

@author: igorvanloo
"""
'''
Project Euler Problem 820

d_n(x) = n-th decimal digit of fractional part of x, or 0 if fractional part has fewer than n digits

lets say 1/x = a.bcde ... n so that the n-th decimal digit is n
then 10^n/x = abcde ... n.op ...

We then have that n = floor(10^n/x) (mod 10) 
                    = floor(10*(10^(n - 1)))/x (mod 10)
                    = floor(10 * (10^(n - 1) (mod x)) / x)
                    
Anwser:
    44967734
'''

def d(n, k):
    return (10 * pow(10, n - 1, k)) // k

def S(n):
    return sum([d(n, k) for k in range(1, n + 1)])

if __name__ == "__main__":
    assert d(7, 1) == 0
    assert d(7, 2) == 0
    assert d(7, 4) == 0
    assert d(7, 5) == 0
    assert d(7, 3) == 3
    assert d(7, 6) == 6
    assert d(7, 7) == 1
    assert S(7) == 10
    assert S(100) == 418
    print(S(10**7))
