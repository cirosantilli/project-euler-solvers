#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00221%20-%20Alexandrian%20Integers.py'''
# -*- coding: utf-8 -*-
"""
Created on Sun May 15 11:20:13 2022

@author: igorvanloo
"""
'''
Project Euler Problem 221

A = p(p + k)((p^2 + 1)/k + p) where k|p^2 + 1 and p is a postive integer

We only need to loop through the first half of the divisors
if p^2 + 1 = ab then 
A_1 = p(p + a)((p^2 + 1)/a + p) = p(p + a)(b + p)
                                        ||
A_2 = p(p + b)((p^2 + 1)/b + p) = p(p + b)(a + p)

'''
import math

def Divisors_of(x):  # Find the divisors of a number
    divisors = []
    for i in range(1, int(math.sqrt(x)) + 1):
        if x % i == 0:
            divisors.append(i)
    return (divisors)

def compute(n=150000):
    alexandrian_integers = []
    p = 1
    target_count = 500000 if n == 150000 else max(50, n * 10)
    while len(alexandrian_integers) < target_count:
        for k in Divisors_of(p*p + 1):
            #print(p, k, p*(p + k)*((p*p + 1)//k + p))
            alexandrian_integers.append(p*(p + k)*((p*p + 1)//k + p))
        p += 1
    return sorted(alexandrian_integers)[n - 1]

if __name__ == "__main__":
    assert compute(6) == 630
    print(compute())
