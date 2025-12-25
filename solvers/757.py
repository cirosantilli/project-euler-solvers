#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00757%20-%20Stealthy%20Numbers.py'''
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 21:46:17 2021

@author: igorvanloo
"""
'''
Project Euler Problem 757

N = ab = cd , a + b = c + d + 1

Let a < b,c,d, x = c - a, y = d - a, then notice 

xy = N -a(c+d) + a^2 = N - a(a+b-1) + a^2 = N - ab + a = a
(x+1)(y+1) = xy + x + y + 1 = a + c - a + d - a + 1 = c + d + 1 - a = b
x(y+1) = xy + x = c
y(x+1) = d

Therefore N = x(x+1)y(y+1)
These are known as Bipronic numbers

For a given x, y can take values y^2 + y < 10^14/(x(x+1)) => x <= y < 1/2*(1+ sqrt(x^2+x+400,000,000,000,000 / (x(x+1))))

Anwser:
    75737353
'''

import math

def Divisors(x): #Find the divisors of a number
    divisors = []
    for i in range(int(math.sqrt(x)),0,-1):
        if x % i == 0:
            divisors.append(i + int(x/i))
    return (divisors)

def compute(limit): #Specific for 10^14 somehow faster? Not sure why
    array = set()
    for x in range(1, int(1/2*(math.sqrt(200000000000001) - 1)) + 1):
        for y in range(x, int(1/2*(math.sqrt((x**2 + x + 400000000000000)/(x*(x+1)))-1)) + 1):
            n = x*(x+1)*y*(y+1)
            if n > limit:
                break
            array.add(n)
            
    return len(array)
    
def compute1(limit): #Faster for lower numbers
    a = set()
    p = []
    for x in range(1, int(math.sqrt(limit))+1):
        p.append(x*(x+1))
        
    for x in p:
        for y in p:
            if x*y > limit:
                break
            a.add(x*y)
            
    return len(a)

def is_stealthy(n):
    for x in range(1, int(math.sqrt(n)) + 1):
        t = x * (x + 1)
        if n % t == 0:
            y = n // t
            r = int((math.isqrt(4 * y + 1) - 1) // 2)
            if r * (r + 1) == y:
                return True
    return False
    
if __name__ == "__main__":
    assert is_stealthy(36)
    assert compute1(10**6) == 2851
    print(compute(10^14))
