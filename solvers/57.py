from typing import Tuple


def count_sqrt2_convergents(limit: int) -> int:
    """
    Count among the first `limit` convergents of sqrt(2) (as in the problem's expansions)
    how many have a numerator with more digits than the denominator.
    """
    # First expansion: 3/2
    p, q = 3, 2
    cnt = 0

    for _ in range(1, limit + 1):
        if len(str(p)) > len(str(q)):
            cnt += 1
        # Next convergent recurrence for sqrt(2) continued fraction:
        # p' = p + 2q
        # q' = p + q
        p, q = p + 2 * q, p + q

    return cnt


def _self_tests() -> None:
    # The 8th expansion 1393/985 is the first where numerator has more digits.
    assert count_sqrt2_convergents(7) == 0
    assert count_sqrt2_convergents(8) == 1


def main() -> None:
    _self_tests()
    result = count_sqrt2_convergents(1000)
    print(result)


if __name__ == "__main__":
    main()
