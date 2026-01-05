#!/usr/bin/env python
"""Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00717%20-%20Summation%20of%20a%20Modular%20Formula.py"""
# -*- coding: utf-8 -*-
"""
Created on Sun May 21 16:36:51 2023

@author: igorvanloo
"""
"""
Project Euler Problem 717

f(p) = floor(2^(2^p) / p) (mod 2^p)
g(p) = f(p) (mod p)
G(N) = sum_{3 <= p <= N} g(p)

Let 2^(2^p) = qp + r, 0 <= r < p, then 
1. q = floor(2^(2^p) / p) = (2^(2^p) - r) / p
2. r = 2^(2^p) (mod p)

Now note that 2^(2^p) = 2^p * 2^(2^p - p) => 2^(2^p) = 0 (mod 2^p)

Therefore f(p) = (2^2^p - r) / p (mod 2^p) = -r / p (mod 2^p) = -r * p^(-1) (mod 2^p)

To compute r:
    1. We remember fermats little theorem, that is 2^(p - 1) = 1 (mod p)
    2. Then 2^(2^p) = 2^(p - 1) * (2^(2^p - (p - 1))) = (2^(2^p - (p - 1)))
        continuing we have that clearly 2^(2^p) = (2^(2^p - n(p - 1)))
    3. Now 2^p - n(p - 1) = x <=> 2^p = x (mod p - 1)
       Therefore we have that r = 2^(2^p) = 2^(2^p (mod p - 1)) (mod p)

To compute p^(-1):
    1. we note that 2^(p - 1) - 1 = 0 (mod p), hence 2^(p - 1) - 1 is a multiple of p
    2. then p*2^(p - 1) - 2^(p - 1) + 1 = (p - 1) * 2^(p - 1) + 1 = 1 (mod 2^p) since p - 1 = 2k
    3. Therefore p*(2^(p - 1) - (2^(p- 1) + 1)/p) = 1 (mod 2^p), this is our inverse
    4. p^(-1) = 2^(p - 1) - (2^(p- 1) + 1)/p = ((p - 1)*2^(p - 1) + 1)/p

then f(p) = -r * ((p - 1)*2^(p - 1) + 1)/p (mod 2^p)

The problem is still calculating 2^p will be too large, but we don't need to do any modulo calculation

Instead note that there is an integer n such that 

0 <= -r * ((p - 1)*2^(p - 1) + 1)/p + n*2^p < 2^p

furthermore, since -r * ((p - 1)*2^(p - 1) + 1)/p = -r * ((p - 1)*2^p + 1)/2p = -r(p-1)2^p/2p - r/2p
we know that x must be the first integer bigger than r(p-1)/2p

so f(p) = -r * ((p - 1)*2^(p - 1) + 1)/p + n*2^p

then g(p) = f(p) (mod p) = 

"""
import math


def list_primality(n):
    result = [True] * (n + 1)
    result[0] = result[1] = False
    for i in range(int(math.sqrt(n)) + 1):
        if result[i]:
            for j in range(2 * i, len(result), i):
                result[j] = False
    return result


def list_primes(n):
    return [i for (i, isprime) in enumerate(list_primality(n)) if isprime]


def g(p):
    x = pow(2, p, p - 1)
    r = pow(2, x, p)
    n = r * (p - 1) // (2 * p) + 1

    pp = pow(2, p - 1, p * p)
    fp = ((-r * (p - 1) * pp + 1) % (p * p)) // p
    return (fp + 2 * n) % p


def G(N):
    primes = list_primes(N)[1:]
    return sum(g(p) for p in primes)


def f_small(p):
    return (pow(2, 2**p) // p) % (2**p)


if __name__ == "__main__":
    assert f_small(3) == 5
    assert g(31) == 17
    assert G(100) == 474
    assert G(10**4) == 2819236
    print(G(10**7))
