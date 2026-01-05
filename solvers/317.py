#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0317.cpp"""
import math

PI = 3.141592653589793238462
G = 9.81


def solve(velocity=20.0, height=100.0):
    add = velocity * velocity / (2 * G) + height
    factor = -G / (2 * velocity * velocity)

    return -0.5 * PI * add * add / factor


def main():
    result = solve()
    print(f"{result:.4f}")


if __name__ == "__main__":
    main()
