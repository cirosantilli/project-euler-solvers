#!/usr/bin/env python
"""Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00318%20-%202011%20nines.py"""
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 16:57:18 2022

@author: igorvanloo
"""
"""
Project Euler Problem 318

Just need to sum ceil(-2011/log_10(p + q - 2sqrt(pq))) if 0 < p + q - 2sqrt(pq) < 1

"""
import math


def compute(limit):
    total = 0
    for p in range(1, limit):
        for q in range(p + 1, limit - p + 1):
            t = p + q - 2 * math.sqrt(p * q)
            if 0 < t < 1:
                total += math.ceil(-limit / math.log(t, 10))
    return total


if __name__ == "__main__":
    print(compute(2011))
