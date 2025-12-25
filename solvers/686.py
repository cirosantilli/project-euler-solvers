#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00686%20-%20Powers%20of%202.py'''
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 23:15:37 2020

@author: igorvanloo
"""
'''
Project Euler Problem 686

2^7 = 128 is the first power of two whose leading digits are "12".
The next power of two whose leading digits are "12" is .

Define p(L, n) to be the nth-smallest value of j such that the base 10 representation of 2^j begins with the digits 
of L

You are also given that p(123, 45) = 12710

Find p(123, 678910)

Through testing I notice the next number such that 2^j starts with 123 is either 196, 289 or 485 away

we are looking for 
2^k = 123.....
2^k = 1.23... * 10^x
log(10)(2^k) = log(10)(1.23... * 10^x)
k*log(10)(2) = log(10)(1.23...) + x

Anwser:
    193060223
    
'''

import math

def p(L, n):
    digits = len(str(L))
    lower = math.log(L, 10) - (digits - 1)
    upper = math.log(L + 1, 10) - (digits - 1)
    cons = math.log(2, 10)
    count = 0
    j = 0
    while count != n:
        j += 1
        temp = j*cons
        if lower < temp - math.floor(temp) < upper:
            count += 1
    return j

def compute(n):
    return p(123, n)
    
if __name__ == "__main__":
    assert p(12, 1) == 7
    assert p(12, 2) == 80
    assert p(123, 45) == 12710
    print(compute(678910))
    

    
