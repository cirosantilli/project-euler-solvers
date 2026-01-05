from typing import *


def digit_sum(n: int) -> int:
    return sum(int(ch) for ch in str(n))


def solve() -> int:
    return digit_sum(2**1000)


def _tests() -> None:
    # Example from the statement
    assert digit_sum(2**15) == 26


if __name__ == "__main__":
    _tests()
    print(solve())
