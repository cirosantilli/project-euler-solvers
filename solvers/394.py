#!/usr/bin/env python3
"""
Project Euler 394 - Eating Pie

We use a closed-form expression for E(x), the expected number of times Jeff repeats
the cutting procedure when the stopping fraction is F = 1/x.

Answer required: E(40) rounded to 10 decimal places.
"""

import math


def expected_repetitions(x: float) -> float:
    """
    Expected number of repetitions for threshold F = 1/x (x >= 1).

    Derived closed form:
        E(x) = 7/9 + (2/3) * ln(x) + 2 / (9 * x^3)
    """
    return 7.0 / 9.0 + (2.0 / 3.0) * math.log(x) + 2.0 / (9.0 * x**3)


def _self_test() -> None:
    # Test values stated in the problem.
    assert abs(expected_repetitions(1.0) - 1.0) < 1e-12
    assert abs(expected_repetitions(2.0) - 1.2676536759) < 1e-10
    assert abs(expected_repetitions(7.5) - 2.1215732071) < 1e-10


def main() -> None:
    _self_test()
    ans = expected_repetitions(40.0)
    print(f"{ans:.10f}")


if __name__ == "__main__":
    main()
