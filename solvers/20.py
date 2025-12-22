from typing import *


def factorial_digit_sum(n: int) -> int:
    fact = 1
    for k in range(2, n + 1):
        fact *= k
    return sum(int(ch) for ch in str(fact))


def main() -> None:
    # Test case from the problem statement
    assert factorial_digit_sum(10) == 27

    result = factorial_digit_sum(100)
    print(result)


if __name__ == "__main__":
    main()
