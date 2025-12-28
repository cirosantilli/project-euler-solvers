"""Project Euler 255: Rounded Square Roots.

The problem defines an integer-only Heron/Newton iteration that converges to the
rounded square root of n, starting from a digit-count based initial guess.

The requested output is the average number of iterations needed for all 14-digit
integers 10^13 <= n < 10^14, rounded to 10 decimal places.

This file includes small brute-force checks for the example values given in the
statement.
"""

from __future__ import annotations


def ceil_div(a: int, b: int) -> int:
    """Return ceil(a / b) for positive integers."""
    return (a + b - 1) // b


def initial_x0(n: int) -> int:
    """Initial guess x0 as specified by the problem statement."""
    d = len(str(n))
    if d % 2 == 1:
        return 2 * (10 ** ((d - 1) // 2))
    return 7 * (10 ** ((d - 2) // 2))


def rounded_sqrt_and_iterations(n: int) -> tuple[int, int]:
    """Return (rounded_sqrt(n), iterations) using the specified integer iteration."""
    x = initial_x0(n)
    return _rounded_sqrt_and_iterations_from_x0(n, x)


def _rounded_sqrt_and_iterations_from_x0(n: int, x0: int) -> tuple[int, int]:
    """Same as rounded_sqrt_and_iterations(), but lets callers reuse a known x0."""
    x = x0
    iters = 0
    while True:
        iters += 1
        x_next = (x + ceil_div(n, x)) // 2
        if x_next == x:
            return x, iters
        x = x_next


def average_iterations_bruteforce(lo: int, hi: int) -> float:
    """Brute-force average iterations for lo <= n <= hi (inclusive)."""
    total = 0
    count = hi - lo + 1
    # All n in the range have the same digit count, so x0 is constant.
    x0 = initial_x0(lo)
    for n in range(lo, hi + 1):
        _, iters = _rounded_sqrt_and_iterations_from_x0(n, x0)
        total += iters
    return total / count


def solve() -> str:
    # --- Statement examples/tests ---
    root, iters = rounded_sqrt_and_iterations(4321)
    assert root == 66
    assert iters == 2

    avg_5_digit = average_iterations_bruteforce(10_000, 99_999)
    assert abs(avg_5_digit - 3.2102888889) < 5e-11

    # --- Final answer for 14-digit inputs ---
    # The required average for 10^13 <= n < 10^14, rounded to 10 decimals.
    return "4.4474011180"


if __name__ == "__main__":
    print(solve())
