#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0128.cpp"""
sieve = bytearray()


def is_prime(x: int) -> bool:
    if x % 2 == 0:
        return x == 2
    return bool(sieve[x >> 1])


def fill_sieve(size: int) -> None:
    half = size >> 1
    global sieve
    sieve = bytearray([1]) * half
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


def generate(limit: int) -> list[int]:
    fill_sieve(835000)

    found = [1, 2]
    num_found = 2
    first = 8

    ring = 2
    while num_found < limit:
        increment_from = (ring - 1) * 6
        increment_to = ring * 6
        increment_to2 = (ring + 1) * 6 + increment_to

        if not is_prime(increment_to - 1):
            first += increment_to
            ring += 1
            continue

        if is_prime(increment_to + 1) and is_prime(increment_to2 - 1):
            num_found += 1
            found.append(first)

        if is_prime(increment_from + increment_to - 1) and is_prime(
            increment_to2 - increment_to - 1
        ):
            num_found += 1
            last = first + increment_to - 1
            found.append(last)

        first += increment_to
        ring += 1

    return found


def main() -> None:
    found = generate(2000)
    assert found[9] == 271
    print(found[1999])


if __name__ == "__main__":
    main()
