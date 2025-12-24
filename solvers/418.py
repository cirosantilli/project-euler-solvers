#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0418.cpp'''
import math

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
factors = []
candidates = {}


def factorize_factorial(factorial):
    global factors
    factors = [0] * len(primes)
    for i in range(2, factorial + 1):
        reduce_value = i
        for idx, p in enumerate(primes):
            while reduce_value % p == 0:
                factors[idx] += 1
                reduce_value //= p


def factorize_number(number):
    global factors
    factors = [0] * len(primes)
    reduce_value = number
    for idx, p in enumerate(primes):
        while reduce_value % p == 0:
            factors[idx] += 1
            reduce_value //= p
        if reduce_value == 1:
            break


def find_candidates(exponents, pos, current, at_least, at_most):
    if pos == len(exponents):
        if current < at_least or current > at_most:
            return
        candidates[current] = exponents[:]
        return

    max_exponent = exponents[pos]
    for exp in range(max_exponent + 1):
        if exp > 0:
            if current * primes[pos] > at_most:
                break
            current *= primes[pos]
            exponents[pos] = exp
        else:
            exponents[pos] = 0

        find_candidates(exponents, pos + 1, current, at_least, at_most)

    exponents[pos] = max_exponent


def search(root3):
    if not candidates:
        return 0

    keys = sorted(candidates)
    best_ratio = keys[-1] / keys[0]

    mid_index = 0
    while mid_index < len(keys) and keys[mid_index] < root3:
        mid_index += 1

    result = 0
    for a_value in keys[:mid_index]:
        a_exp = candidates[a_value]
        for c_value in keys[mid_index:]:
            if a_value * best_ratio < c_value:
                break

            is_valid = True
            b = 1
            for i in range(len(primes)):
                used = a_exp[i] + candidates[c_value][i]
                if used > factors[i]:
                    is_valid = False
                    break
                while used < factors[i]:
                    b *= primes[i]
                    used += 1

            if not is_valid:
                continue

            if b < a_value or b > c_value:
                continue

            ratio = c_value / a_value
            if ratio < best_ratio:
                best_ratio = ratio
                result = a_value + b + c_value

            break

    return result


def solve_number(number, max_ratio=0.0002):
    candidates.clear()
    factorize_number(number)

    at_least = 1 - max_ratio / 2
    at_most = 1 + max_ratio / 2

    root3 = number ** (1.0 / 3.0)
    find_candidates(factors[:], 0, 1, root3 * at_least, root3 * at_most)
    return search(root3)


def solve_factorial(limit=43, max_ratio=0.0002):
    candidates.clear()
    factorize_factorial(limit)

    at_least = 1 - max_ratio / 2
    at_most = 1 + max_ratio / 2

    factorial_value = math.factorial(limit)
    root3 = factorial_value ** (1.0 / 3.0)

    find_candidates(factors[:], 0, 1, root3 * at_least, root3 * at_most)
    return search(root3)


def main():
    assert solve_number(165) == 19
    assert solve_number(100100) == 142
    assert solve_factorial(20) == 4034872
    print(solve_factorial(43))


if __name__ == "__main__":
    main()
