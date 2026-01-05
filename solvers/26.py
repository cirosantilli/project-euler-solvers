from typing import Tuple


def recurring_cycle_length(d: int) -> int:
    """
    Length of the recurring cycle in the decimal expansion of 1/d.
    """
    # Remove factors of 2 and 5 (they only affect the terminating part)
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5

    # If what's left is 1, the decimal terminates => no recurring cycle
    if d == 1:
        return 0

    # Now gcd(d, 10) = 1; cycle length is the multiplicative order of 10 mod d
    k = 1
    r = 10 % d
    while r != 1:
        r = (r * 10) % d
        k += 1
    return k


def solve(limit: int = 1000) -> int:
    best_d = 0
    best_len = -1
    for d in range(2, limit):
        L = recurring_cycle_length(d)
        if L > best_len:
            best_len = L
            best_d = d
    return best_d


def _tests() -> None:
    # Examples from the statement
    assert recurring_cycle_length(2) == 0
    assert recurring_cycle_length(3) == 1
    assert recurring_cycle_length(4) == 0
    assert recurring_cycle_length(5) == 0
    assert recurring_cycle_length(6) == 1
    assert recurring_cycle_length(7) == 6
    assert recurring_cycle_length(8) == 0
    assert recurring_cycle_length(9) == 1
    assert recurring_cycle_length(10) == 0


def main() -> None:
    _tests()
    print(solve(1000))


if __name__ == "__main__":
    main()
