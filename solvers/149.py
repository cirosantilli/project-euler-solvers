#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0149.cpp"""
SIZE = 2000


def fill_lagged_fibonacci(length: int) -> list[int]:
    data = [0] * length
    k = 1
    for idx in range(min(55, length)):
        val = (100003 - 200003 * k + 300007 * k * k * k) % 1000000 - 500000
        data[idx] = val
        k += 1

    for idx in range(55, length):
        data[idx] = (data[idx - 24] + data[idx - 55] + 1000000) % 1000000 - 500000

    return data


def max_sum(data: list[int], first: int, last: int, increment: int) -> int:
    result = data[first]
    current_sum = 0
    i = first
    while i <= last:
        current_sum += data[i]
        if current_sum < 0:
            current_sum = 0
        if result < current_sum:
            result = current_sum
        i += increment
    return result


def index(x: int, y: int) -> int:
    return y * SIZE + x


def solve(size: int) -> int:
    data = fill_lagged_fibonacci(size * size)

    last = size - 1
    result = data[0]

    for y in range(size):
        current = max_sum(data, y * size, y * size + last, 1)
        if result < current:
            result = current

    for x in range(size):
        current = max_sum(data, x, last * size + x, size)
        if result < current:
            result = current

    for x in range(size):
        current = max_sum(data, x, (last - x) * size + last, size + 1)
        if result < current:
            result = current

    for y in range(1, size):
        current = max_sum(data, y * size, last * size + y, size + 1)
        if result < current:
            result = current

    for x in range(size):
        current = max_sum(data, x, x * size, size - 1)
        if result < current:
            result = current

    for y in range(1, size):
        current = max_sum(data, y * size + last, last * size + y, size - 1)
        if result < current:
            result = current

    return result


def main() -> None:
    sequence = fill_lagged_fibonacci(100)
    assert sequence[9] == -393027
    assert sequence[99] == 86613
    print(solve(SIZE))


if __name__ == "__main__":
    main()
