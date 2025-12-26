#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00684%20-%20Inverse%20Digit%20sum.py'''
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 09:56:17 2020

@author: igorvanloo
"""

'''
Project Euler Problem 684

Anwser:
    922058210
    
'''

import math


def fibonnaci(x):
    if x == 1:
        return 1
    if x == 2:
        return 1
    
    f1 = 1
    f2 = 1
    fib_numbers = [0, f1, f2]
    while len(fib_numbers) < x:
        fn = f1 + f2
        fib_numbers.append(fn)
        f1 = f2
        f2 = fn
    return fib_numbers

def sn(b):
    return ((b % 9 + 1)*(pow(10,(b // 9), 1000000007)) - 1) % 1000000007

def s(n):
    q, r = divmod(n, 9)
    if r == 0:
        return int("9" * q)
    return int(str(r) + "9" * q)

def S(k, mod):
    q = k // 9
    r = k % 9
    sum1 = (6*(pow(10,q,mod) - 1)) - (9*q % mod)
    sum2 = sum([i*pow(10,q,mod) - 1 for i in range(2,r+2)])
    return (sum1+sum2) % mod

def finals(k):
    q = k // 9
    r = k % 9
    
    return (6*(pow(10,q,1000000007) - 1) - (9*q % 1000000007) + (r/2)*(r*pow(10,q,1000000007) + 3*pow(10,q,1000000007) - 2)) % 1000000007

def compute1():
    total = 0
    temp_list = fibonnaci(92)
    for x in range(2,91):
        total += finals(temp_list[x])
    return int(total % 1000000007)

if __name__ == "__main__":
    assert s(10) == 19
    assert S(20, 10**18) == 1074
    print(compute1())
