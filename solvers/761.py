#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00761%20-%20Runner%20and%20Swimmer.py'''
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 00:37:09 2023

@author: igorvanloo
"""
'''
Project Euler Problem 761

Anwser:
    5.05505046
'''
from sympy import sin, cos, tan, pi, acos
    
def compute(n):
    K = 0
    theta = pi/n
    f = lambda k : sin(k*theta) - (k + n)*tan(theta)*cos(k*theta)
    
    while f(K) < 0:
        K += 1
    K -= 1
    a = (K*theta + acos(2*sin(K*theta)/((K + n)*tan(theta)) -cos(K*theta)))/2
    return round(1/cos(a), 8)

if __name__ == "__main__":
    print(compute(6))
