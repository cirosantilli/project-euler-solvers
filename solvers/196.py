#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0196.cpp"""
import math

sieve = bytearray()
segment = []
segment_start = 0


def fill_sieve(size: int) -> None:
    half = (size >> 1) + 1
    if len(sieve) >= half:
        return
    sieve.extend([1] * (half - len(sieve)))
    sieve[0] = 0

    i = 1
    while 2 * i * i < half:
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = 0
                current += step
        i += 1


def is_prime(x: int) -> bool:
    if x % 2 == 0:
        return x == 2
    return bool(sieve[x >> 1])


def get_number(x: int, y: int) -> int:
    return x + y * (y - 1) // 2


def fill_segmented_sieve(from_val: int, to_val: int) -> None:
    fill_sieve(int(math.isqrt(to_val)))

    global segment_start, segment
    segment_start = from_val | 1
    num_values = to_val - from_val + 1
    segment = [True] * (num_values + 1)

    for p in range(3, int(math.isqrt(to_val)) + 1, 2):
        if is_prime(p):
            smallest = from_val - (from_val % p) + p
            if smallest % 2 == 0:
                smallest += p
            for i in range(smallest, to_val + 1, 2 * p):
                segment[(i - segment_start) // 2] = False


def is_prime_in_segment(x: int, y: int) -> bool:
    if x < 1 or x > y:
        return False

    current = get_number(x, y)
    if current % 2 == 0:
        return current == 2

    return segment[(current - segment_start) // 2]


def process_line(line: int) -> int:
    sieve_from = get_number(1, line - 2)
    sieve_to = get_number(1, line + 3) - 1
    if line <= 2:
        sieve_from = 1

    fill_segmented_sieve(sieve_from, sieve_to)

    three_plus = [False] * len(segment)
    for y in range(line - 1, line + 2):
        for x in range(1, y + 1):
            if not is_prime_in_segment(x, y):
                continue

            count_primes = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if count_primes < 3 and is_prime_in_segment(x + dx, y + dy):
                        count_primes += 1
            three_plus[get_number(x, y) - segment_start] = count_primes >= 3

    total = 0
    for x in range(1, line + 1):
        current = get_number(x, line)
        if not is_prime_in_segment(x, line):
            continue

        at_least_three = False
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                at_least_three |= three_plus[
                    get_number(x + dx, line + dy) - segment_start
                ]

        if at_least_three:
            total += current

    return total


def main() -> None:
    assert process_line(8) == 60
    assert process_line(9) == 37
    assert process_line(10000) == 950007619

    one = 5678027
    two = 7208785
    print(process_line(one) + process_line(two))


if __name__ == "__main__":
    main()
