#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00751%20-%20Concatenation%20Coincidence.py'''
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 21:00:17 2021

@author: igorvanloo
"""

'''
Project Euler Problem 751

theta = 2.956938891377988

a1 = 2 => 2 < theta < 3
theta = 2.1, tau = 2.222...
theta = 2.2, tau = 2.2234...
theta = 2.3, tau = 2.23...

So we pick theta = 2.2
Repeat

Anwser:
    2.223561019313554106173177
'''

import math

def sequence(theta, length):
    b1 = theta
    tau = str(math.floor(b1)) + "."
    
    while len(tau) < (length):
        floorb1 = math.floor(b1)
        bn = floorb1 * (b1 - floorb1 + 1)
        tau += str(math.floor(bn))
        b1 = bn
    return (tau[:length])

def compute(length):
    curr = "2."
    while len(curr) <= length:
        for x in range(0, 10):
            temp_curr = curr + str(x)
            if (temp_curr) == sequence(float(temp_curr), len(temp_curr)):
                curr += str(x)                
    return (curr)[:length]

def sequence_terms(theta, count):
    b = theta
    terms = []
    for _ in range(count):
        a = math.floor(b)
        terms.append(a)
        b = a * (b - a + 1)
    return terms

if __name__ == "__main__":
    assert sequence_terms(2.956938891377988, 5) == [2, 3, 5, 8, 13]
    print(compute(26))
