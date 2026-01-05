#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0225.cpp"""


def solve(index: int) -> int:

    max_steps = 22710

    current = 1
    num_found = 0
    while num_found < index:
        current += 2

        tri1 = 1
        tri2 = 1
        tri3 = 1

        is_divisor = False
        for _ in range(max_steps + 1):
            tri_next = tri1 + tri2 + tri3
            tri_next %= current

            if tri_next == 0:
                is_divisor = True
                break

            tri1, tri2, tri3 = tri2, tri3, tri_next

            if tri1 == 1 and tri2 == 1 and tri3 == 1:
                break

        if not is_divisor:
            num_found += 1

    return current


def main() -> None:
    assert solve(1) == 27
    print(solve(124))


if __name__ == "__main__":
    main()
