#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0333.cpp"""
sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = (size >> 1) + 1
    sieve = [True] * half
    if half > 0:
        sieve[0] = False

    i = 1
    while 2 * i * i < half:
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = False
                current += step
        i += 1


def power(exp_two, exp_three):
    result = 1
    base = 3
    while exp_three > 0:
        if exp_three & 1:
            result *= base
        base *= base
        exp_three >>= 1
    return result << exp_two


def solve(limit=1000000):
    num_power_two = 0
    num_power_three = 0
    while power(num_power_two, 0) <= limit:
        num_power_two += 1
    while power(0, num_power_three) <= limit:
        num_power_three += 1

    too_large = 0
    next_id = 1
    ids = [[too_large for _ in range(num_power_three)] for _ in range(num_power_two)]
    reverse_id = [None]

    for exp_two in range(num_power_two):
        for exp_three in range(num_power_three):
            current = power(exp_two, exp_three)
            if current <= limit:
                reverse_id.append((exp_two, exp_three))
                ids[exp_two][exp_three] = next_id
                next_id += 1
            else:
                ids[exp_two][exp_three] = too_large

    reachable = [bytearray(limit + 1) for _ in range(next_id)]
    multiple = [bytearray(limit + 1) for _ in range(next_id)]

    for idx in range(1, len(reverse_id)):
        exp_two, exp_three = reverse_id[idx]
        value = power(exp_two, exp_three)
        reachable[idx][value] = 1

    fill_sieve(limit)
    total = 0
    for value in range(1, limit + 1):
        possible = False
        unique = True

        for idx in range(1, len(reverse_id)):
            exp_two, exp_three = reverse_id[idx]
            if reachable[idx][value] == 0:
                continue

            if possible or multiple[idx][value]:
                unique = False
            possible = True

            next_exp_two = exp_two + 1
            while next_exp_two < num_power_two:
                next_exp_three = 0
                while next_exp_three < exp_three:
                    next_id_value = ids[next_exp_two][next_exp_three]
                    if next_id_value == too_large:
                        break
                    next_value = value + power(next_exp_two, next_exp_three)
                    if next_value > limit:
                        break

                    if reachable[next_id_value][next_value]:
                        multiple[next_id_value][next_value] = 1
                    else:
                        reachable[next_id_value][next_value] = 1

                    next_exp_three += 1
                next_exp_two += 1

        if possible and unique and is_prime(value):
            total += value

    return total


def main():
    assert solve(100) == 233
    print(solve())


if __name__ == "__main__":
    main()
