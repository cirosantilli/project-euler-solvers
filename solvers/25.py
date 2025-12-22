from typing import Tuple


def first_fib_index_with_digits(digits: int) -> int:
    """
    Returns the smallest n such that Fibonacci number F_n has at least `digits` decimal digits.
    Fibonacci is defined as: F_1 = 1, F_2 = 1, F_n = F_{n-1} + F_{n-2}.
    """
    assert digits >= 1

    a, b = 1, 1  # F_1, F_2
    if digits == 1:
        return 1

    n = 2
    while len(str(b)) < digits:
        a, b = b, a + b
        n += 1
    return n


def main() -> None:
    # Tests implied by the statement / known small cases
    assert first_fib_index_with_digits(1) == 1  # F_1 = 1
    assert first_fib_index_with_digits(2) == 7  # F_7 = 13
    assert first_fib_index_with_digits(3) == 12  # F_12 = 144

    ans = first_fib_index_with_digits(1000)
    print(ans)


if __name__ == "__main__":
    main()
