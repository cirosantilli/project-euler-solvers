#!/usr/bin/env python
"""Adapted from https://github.com/igorvanloo/Project-Euler-Explained/blob/main/pe00700%20-%20Eulercoin.py"""
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 10:43:07 2020

@author: igorvanloo
"""

"""
Project Euler Problem 700

Leonhard Euler was born on 15 April 1707.

Consider the sequence 1504170715041707n mod 4503599627370517.

An element of this sequence is defined to be an Eulercoin if it is strictly smaller than all previously 
found Eulercoins.

For example, the first term is 1504170715041707 which is the first Eulercoin. The second term is 
3008341430083414 which is greater than 1504170715041707 so is not an Eulercoin. However, the third term is 
8912517754604 which is small enough to be a new Eulercoin.

The sum of the first 2 Eulercoins is therefore 1513083232796311.

Find the sum of all Eulercoins.

"""


def compute():
    eulercoins = [1504170715041707]
    current_eulercoin = 1504170715041707
    inv = pow(1504170715041707, -1, 4503599627370517)
    n = 2
    while True:
        number = 1504170715041707 * n % 4503599627370517
        if number < current_eulercoin:
            current_eulercoin = number
            eulercoins.append(number)
            print(n, number)
        if current_eulercoin == 15806432:
            print("x")
            new_curr_eulercoin = 1
            curr_max = 4503599627370517
            while new_curr_eulercoin != 15806432:

                number = (inv * new_curr_eulercoin) % 4503599627370517

                if number < curr_max:
                    curr_max = number
                    eulercoins.append(new_curr_eulercoin)
                    print(number, new_curr_eulercoin)

                new_curr_eulercoin += 1
            break
        n += 1

    return sum(eulercoins)


def maxminmethod():
    mod = 4503599627370517
    maxe = 1504170715041707
    mine = 1504170715041707
    total = 1504170715041707

    while True:
        if mine == 1:
            break
        middle = (maxe + mine) % mod

        if middle > maxe:
            maxe = middle

        if middle < mine:
            mine = middle
            # print(mine)
            total += mine
    return total


def first_eulercoins(count):
    mod = 4503599627370517
    k = 1504170715041707
    eulercoins = []
    current_min = mod
    n = 1
    while len(eulercoins) < count:
        value = (k * n) % mod
        if value < current_min:
            eulercoins.append(value)
            current_min = value
        n += 1
    return eulercoins


if __name__ == "__main__":
    coins = first_eulercoins(2)
    assert coins[0] == 1504170715041707
    assert sum(coins) == 1513083232796311
    print(compute())
    # print(maxminmethod())
