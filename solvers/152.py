#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0152.cpp'''
from collections import Counter
from fractions import Fraction


TARGET_SUM = Fraction(1, 2)
last_number_threshold = 40
candidates: list[int] = []
last_numbers: Counter = Counter()
remaining: dict[int, Fraction] = {}


members: list[int] = []


def search(current: Fraction = Fraction(0, 1), next_index: int = 0) -> int:
    if current == TARGET_SUM:
        return 1
    if TARGET_SUM < current:
        return 0
    if next_index == len(candidates):
        return 0

    number = candidates[next_index]

    maximum = current + remaining[number]
    if maximum < TARGET_SUM:
        return 0

    if number >= last_number_threshold:
        difference = TARGET_SUM - current
        return last_numbers[difference]

    result = 0
    result += search(current, next_index + 1)

    add = Fraction(1, number * number)
    members.append(number)
    result += search(current + add, next_index + 1)
    members.pop()

    return result


def solve(denominator: int, limit: int) -> int:
    global TARGET_SUM
    TARGET_SUM = Fraction(1, denominator)

    primes = []
    for i in range(2, limit + 1):
        is_prime = True
        for j in range(2, int(i ** 0.5) + 1):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)

    relevant_prime = set()
    found = [False] * (limit + 1)
    for p in primes:
        multiples = [Fraction(1, m * m) for m in range(p, limit + 1, p)]
        combinations = 1 << len(multiples)
        for mask in range(1, combinations):
            current = Fraction(0, 1)
            for pos in range(len(multiples)):
                if mask & (1 << pos):
                    current += multiples[pos]
            if current.denominator % p == 0:
                continue

            for pos in range(len(multiples)):
                if mask & (1 << pos):
                    is_good = (pos + 1) * p
                    found[is_good] = True

            relevant_prime.add(p)
            found[p] = True

            if p < 5:
                break

    two = 1
    while two <= limit:
        three = 1
        while two * three <= limit:
            found[two * three] = True
            three *= 3
        two *= 2

    for i in range(2, limit + 1):
        if not found[i]:
            continue

        reduce = i
        for p in relevant_prime:
            while reduce % p == 0:
                reduce //= p

        if reduce != 1:
            found[i] = False
            continue

        candidates.append(i)

    running = Fraction(0, 1)
    for current in reversed(candidates):
        running += Fraction(1, current * current)
        remaining[current] = running

    global last_number_threshold
    last_number_threshold = limit // 2
    last_start = 0
    while last_start < len(candidates) and candidates[last_start] < last_number_threshold:
        last_start += 1

    num_last_numbers = len(candidates) - last_start
    combinations = 1 << num_last_numbers
    for mask in range(combinations):
        current = Fraction(0, 1)
        for pos in range(num_last_numbers):
            if mask & (1 << pos):
                add = candidates[last_start + pos]
                current += Fraction(1, add * add)
        last_numbers[current] += 1

    return search()


def main() -> None:
    assert solve(2, 45) == 3
    print(solve(2, 80))


if __name__ == "__main__":
    main()
