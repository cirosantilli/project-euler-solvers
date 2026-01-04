#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00697%20-%20Randomly%20Decaying%20Sequences.py'''
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 18:24:52 2022

@author: igorvanloo
"""

'''
Project Euler Problem 697

log is in the question so I assume we need to use it somehow

We are looking for 

P(X_10,000,000 < 1) = 0.25 <=>
P(U_10,000,000 * U_9,999,999 * ... * U_1 * c < 1) = 0.25 <=>
P(U_10,000,000 * U_9,999,999 * ... * U_1 < 1/c) = 0.25 <=>

If X ~ Unif(0,1) then Y = -y^-1 ln(X) is Y ~ exp(y), so we take y = 1

P(-ln(U_10,000,000 * U_9,999,999 * ... * U_1) > -ln(1/c)) = 0.25 <=>
P(-ln(U_10,000,000) - ln(U_9,999,999) - ... - ln(U_1) > -ln(1/c)) = 0.25 <=>

sum of n exponential variables is a gamma distribution Γ(n, 1)

P(Γ(10,000,000, 1) > -ln(1/c)) = 0.25 <=>
P(Γ(10,000,000, 1) > ln(c)) = 0.25 <=>

then we find ln(c) and our answer is ln(c)/ln(10)

Then I used an online tool https://homepage.divms.uiowa.edu/~mbognar/applets/gamma.html and wolfram alpha

'''
    
from math import log, sqrt

def compute(n):
    # Wilson-Hilferty approximation for chi-square; Gamma(n,1) => 2*X ~ chi2(2n)
    z = 0.6744897501960817  # Normal(0,1) 75th percentile
    df = 2.0 * n
    chi2_ppf = df * (1.0 - 2.0 / (9.0 * df) + z * sqrt(2.0 / (9.0 * df))) ** 3
    return round((0.5 * chi2_ppf) / log(10), 2)

if __name__ == "__main__":
    assert compute(100) == 46.27
    print(compute(10**7))
