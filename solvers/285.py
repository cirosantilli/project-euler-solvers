#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00285%20-%20Pythagorean%20odds.py'''
# -*- coding: utf-8 -*-
"""
Created on Sun May 29 23:29:01 2022

@author: igorvanloo
"""
'''
Project Euler Problem 

The probability we win can be mapped inside a torus

(sqrt((k - 0.5)^2 - (k*x + 1)^2) - 1)/k ≤ y ≤ (sqrt((k + 0.5)^2 - (k*x + 1)^2) - 1)/k

Anwser:
    157055.80999
'''
import math
    
def compute(limit):
    def area_under_circle(k, r):
        u_max = math.sqrt(r * r - 1.0)
        def primitive(u):
            return 0.5 * (u * math.sqrt(r * r - u * u) + r * r * math.asin(u / r))
        return (primitive(u_max) - primitive(1.0) - (u_max - 1.0)) / (k * k)
    total = area_under_circle(1, 1.5)
    for k in range(2, limit + 1):
        area_under_upper_circle = area_under_circle(k, k + 0.5)
        area_under_lower_circle = area_under_circle(k, k - 0.5)
        total += k * (area_under_upper_circle - area_under_lower_circle)
    return round(total, 5)

if __name__ == "__main__":
    assert compute(10) == 10.20914
    print(compute(10**5))
