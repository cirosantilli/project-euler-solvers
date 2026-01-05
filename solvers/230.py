#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0230.cpp"""


def build_fibonacci(block_size: int) -> list[int]:
    fibonacci = [0, block_size]
    while fibonacci[-1] < (1 << 63):
        fibonacci.append(fibonacci[-2] + fibonacci[-1])
    return fibonacci


def digit_at(A: str, B: str, index: int, fibonacci: list[int]) -> str:
    current = 1
    while index >= fibonacci[current]:
        current += 1

    while True:
        if current == 1:
            return A[index]
        if current == 2:
            return B[index]

        mid = fibonacci[current - 2]
        if index < mid:
            current -= 2
        else:
            index -= mid
            current -= 1


def solve(A: str, B: str) -> str:
    block_size = len(A)
    fibonacci = build_fibonacci(block_size)

    output = []
    for n in range(17, -1, -1):
        index = 127 + 19 * n
        for _ in range(1, n + 1):
            index *= 7
        index -= 1
        output.append(digit_at(A, B, index, fibonacci))

    return "".join(output)


def main() -> None:
    example_A = "1415926535"
    example_B = "8979323846"
    example_fib = build_fibonacci(len(example_A))
    assert digit_at(example_A, example_B, 35 - 1, example_fib) == "9"

    A = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
    B = "8214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
    print(solve(A, B))


if __name__ == "__main__":
    main()
