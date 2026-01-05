#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0206.cpp"""


def match(x: int) -> bool:
    square = x * x
    right_to_left = [0, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    index = 0

    while square > 0:
        digit = square % 10
        if digit != right_to_left[index]:
            return False
        index += 1
        square //= 100

    return True


def main() -> None:
    min_number = 1010101010
    max_number = 1389026620

    for x in range(max_number, min_number - 1, -10):
        if match(x):
            print(x)
            break


if __name__ == "__main__":
    main()
