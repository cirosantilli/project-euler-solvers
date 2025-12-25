#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00577%20-%20Counting%20Hexagons.py'''
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 21:06:20 2021

@author: igorvanloo
"""

'''
Project Euler Problem 577

H(3) = 1 = T(1)
H(4) = 3 = T(2)
H(5) = 6 = T(3)
H(6) = 12 = T(4) + 2T(1)
H(7) = 21 = T(5) + 2T(2)

H(20) = T(18) + 2T(15) + 3T(12) + 4T(9) + 5T(6) + 6T(3)

In general every time H(3n) we add n new types of hexagons

H(3) we have a 1 side length hexagons
H(6) we have 2 side length and also sqrt(3) side length 

Anwser:
    265695031399260211
'''


def H(n, tri_numbers):
    total = 0
    for y in range(1, n//3 + 1):
        total += y * tri_numbers[n - 2 - 3*(y - 1)]
    return total

def compute(limit):
    total = 0
    tri_numbers = [0] + [int((n*(n+1))/2) for n in range(1, 12344)]
    
    for x in range(3, limit + 1):
        total += H(x, tri_numbers)
    return total
        
if __name__ == "__main__":
    tri_numbers = [0] + [int((n*(n+1))/2) for n in range(1, 12344)]
    assert H(3, tri_numbers) == 1
    assert H(6, tri_numbers) == 12
    assert H(20, tri_numbers) == 966
    print(compute(12345))
