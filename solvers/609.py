#!/usr/bin/env python
"""Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00609%20-%20pi%20sequences.py"""
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 20:49:49 2021

@author: igorvanloo
"""

"""
Project Euler Problem 609

pi(n) = number of primes not exceeding n
u = (u_0, u_1, ..., u_n)

pi sequence if 
1. u_n ≥ 1 for all n
2. u_{n+1} = pi(u_n)
3. u has more than 2 elements

c(u) = number of elements in u that are not prime
p(n,k) = the number of pi sequence such that u_0 ≤ n and c(u) = k
P(n) = product of all p(n,k) ≥ 0

First thing to notice is u is deteremined by u_0, an array with all the pi(n) may be necessary


    742870469 ~ 10^7

~ 10^8
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


def P(limit, mod=1000000007):
    prime_gen = list_primality(limit + 50)
    primes = [x for x in range(len(prime_gen)) if prime_gen[x]]

    print("Primes done")
    array = [0] * (limit + 1)
    p_index = 0
    for x in range(1, limit + 1):
        while True:
            if primes[p_index] > x:
                array[x] = p_index
                break
            p_index += 1
    print("Array done")

    array2 = [0] * (limit + 1)
    for x in range(1, limit + 1):
        if x % 1000000 == 0:
            print(x)
        prime_non_count = 0
        if prime_gen[x] == False:
            prime_non_count += 1
        curr = x
        while True:
            temp = array[curr]
            if temp == 0:
                break
            else:
                if prime_gen[temp] == False:
                    prime_non_count += 1

            array2[prime_non_count] += 1
            curr = temp

    print("array2 done")

    total = 1
    for x in array2:
        if x != 0:
            total *= x
            if mod is not None:
                total %= mod
    return total if mod is None else total % mod


if __name__ == "__main__":
    assert P(10, mod=None) == 648
    assert P(100, mod=None) == 31038676032
    print(P(10**8))
