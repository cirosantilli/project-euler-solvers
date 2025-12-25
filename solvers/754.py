#!/usr/bin/env python
'''Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00754%20-%20Product%20of%20Gauss%20Factorials.py'''
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 22:06:30 2021

@author: igorvanloo
"""
'''
Project Euler Problem 754

After some brute force found

g(n) = https://oeis.org/A001783

g(n) = n^phi(n)*Product_{d|n} (d!/d^d)^mu(n/d)

    517055464 ~ 10^4
    516871211 ~ 10^5
    557051244 ~ 10^6
    623561178 ~ 10^7

Anwser:
    785845900
'''
import math


def totient_mobius_sieve(n):
    phi = [i for i in range(n + 1)]
    mob = [1]*(n + 1)
    mob[0] = 0
    for p in range(2, n + 1):
        if phi[p] == p:
            # print(p)
            for i in range(p, n + 1, p):
                phi[i] -= (phi[i] // p)
                mob[i] *= -1
            sq = p*p
            if sq < n:
                for j in range(sq, n + 1, sq):
                    mob[j] = 0
    return phi, mob

def modfactorial(limit, mod):
    factorial = [1]*(limit + 1)
    for x in range(2, limit):
        factorial[x] = x*factorial[x - 1]
        factorial[x] %= mod
    return factorial

def ModDivision(a,b,m):
    a = a % m
    try:
        inv = pow(b,-1,m)
    except ValueError:
        return "Division not defined"
    else:
        return (inv*a) % m

def g(n):
    total = 1
    for i in range(1, n + 1):
        if math.gcd(i, n) == 1:
            total *= i
    return total

def G_small(n):
    total = 1
    for i in range(1, n + 1):
        total *= g(i)
    return total

def compute(limit, mod):
    phi_sieve, mu_sieve = totient_mobius_sieve(limit)
    factorial = modfactorial(limit, mod)
    G = 1
    for n in range(0, limit + 1):
        G *= pow(n, phi_sieve[n], mod)
        G %= mod
    for d in range(2, limit + 1):
        fac = ModDivision(factorial[d - 1], pow(d, d - 1, mod), mod)
        mu_total = sum(mu_sieve[n//d] for n in range(d, limit + 1, d))
        G *= pow(fac, mu_total, mod)
        G %= mod
    return G

if __name__ == "__main__":
    assert g(10) == 189
    assert G_small(10) == 23044331520000
    print(compute(10**8, 10**9 + 7))
