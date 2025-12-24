#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0307.cpp'''
import math


def myrand():
    myrand.seed = (6364136223846793005 * myrand.seed + 1) & ((1 << 64) - 1)
    return myrand.seed >> 30


myrand.seed = 0


def monte_carlo(iterations, k, n):
    threshold = 3
    bad = 0
    defects = [0] * n
    for _ in range(iterations):
        for i in range(n):
            defects[i] = 0

        for _ in range(k):
            idx = myrand() % n
            defects[idx] += 1
            if defects[idx] == threshold:
                bad += 1
                break

    return bad / float(iterations)


def log_factorial(n):
    result = 0.0
    for i in range(2, n + 1):
        result += math.log(i)
    return result


def log_factorial_top(n, only_top_values):
    result = 0.0
    start = n - only_top_values + 1
    for i in range(start, n + 1):
        result += math.log(i)
    return result


def solve(defects: int, chips: int) -> float:
    precision_threshold = 1e-13

    combinations = math.log(chips) * defects

    total = 0.0
    for num_two_defects in range(defects // 2 + 1):
        affected_chips = defects - num_two_defects
        permutations = log_factorial_top(chips, affected_chips)

        defects_on_twos = 2 * num_two_defects
        count = log_factorial_top(defects, defects_on_twos)
        count -= log_factorial(num_two_defects)
        count -= num_two_defects * math.log(2.0)

        no_defects = permutations + count
        ratio = no_defects - combinations
        ratio = math.exp(ratio)
        total += ratio

        if total > 0.01 and ratio < precision_threshold:
            break

    result = 1.0 - total
    return result


if __name__ == "__main__":
    assert f"{solve(3, 7):.10f}" == "0.0204081633"
    print(f"{solve(20000, 1000000):.10f}")
