from __future__ import annotations

from typing import Tuple


def digit_sum(n: int) -> int:
    return sum(ord(ch) - 48 for ch in str(n))


def max_digital_sum(limit: int) -> Tuple[int, int, int]:
    """
    Returns (best_sum, best_a, best_b) for 1 <= a,b < limit.
    """
    best = -1
    best_a = -1
    best_b = -1
    for a in range(1, limit):
        for b in range(1, limit):
            s = digit_sum(pow(a, b))
            if s > best:
                best = s
                best_a = a
                best_b = b
    return best, best_a, best_b


def main() -> None:
    # Basic sanity checks
    assert digit_sum(10**100) == 1
    assert digit_sum(2**15) == 26
    best, a, b = max_digital_sum(100)
    print(best)


if __name__ == "__main__":
    main()
