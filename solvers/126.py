#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0126.cpp"""
FAILED = 0


def hull_volume(x: int, y: int, z: int, layers: int) -> int:
    result = 2 * (x * y + y * z + z * x)
    if layers == 1:
        return result
    increment = 4 * (x + y + z)
    for _ in range(2, layers + 1):
        result += increment
        increment += 8
    return result


def fast(stop_if: int, max_volume: int) -> int:
    count = [0] * (max_volume + 1)

    x = 1
    while hull_volume(x, 1, 1, 1) <= max_volume:
        y = 1
        while y <= x and hull_volume(x, y, 1, 1) <= max_volume:
            z = 1
            while z <= y and hull_volume(x, y, z, 1) <= max_volume:
                result = 2 * (x * y + y * z + z * x)
                increment = 4 * (x + y + z)
                while result <= max_volume:
                    count[result] += 1
                    result += increment
                    increment += 8
                z += 1
            y += 1
        x += 1

    for i, value in enumerate(count):
        if value == stop_if:
            return i

    return FAILED


def counts_up_to(max_volume: int) -> list[int]:
    count = [0] * (max_volume + 1)
    x = 1
    while hull_volume(x, 1, 1, 1) <= max_volume:
        y = 1
        while y <= x and hull_volume(x, y, 1, 1) <= max_volume:
            z = 1
            while z <= y and hull_volume(x, y, z, 1) <= max_volume:
                result = 2 * (x * y + y * z + z * x)
                increment = 4 * (x + y + z)
                while result <= max_volume:
                    count[result] += 1
                    result += increment
                    increment += 8
                z += 1
            y += 1
        x += 1
    return count


def main() -> None:
    count = counts_up_to(118)
    assert count[22] == 2
    assert count[46] == 4
    assert count[78] == 5
    assert count[118] == 8
    assert fast(10, 2000) == 154

    stop_if = 1000
    step_size = 10000
    max_volume = step_size
    while True:
        current = fast(stop_if, max_volume)
        if current != FAILED:
            print(current)
            return
        max_volume += step_size


if __name__ == "__main__":
    main()
