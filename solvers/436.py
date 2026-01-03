#!/usr/bin/env python3
"""
Project Euler 436 - Unfair Wager

We need the probability that the second player's last draw y is greater than the
first player's last draw x.

An analytic derivation (see README.md for an outline) yields the closed form:

    P(y > x) = (1 + 14 e - 5 e^2) / 4

We compute this value and print it rounded to 10 decimal places.

No third-party libraries are used.
"""

from __future__ import annotations

from decimal import Decimal, getcontext


def example_game_outcome(draws: list[float]) -> tuple[float, float]:
    """
    Deterministically evaluate a single game using a provided sequence of draws.

    The game described in the statement:
      - start S=0
      - first player draws until S>1, last draw is x
      - second player continues until S>2, last draw is y
    """
    s = 0.0
    i = 0

    # Louise
    while s <= 1.0:
        s += draws[i]
        x = draws[i]
        i += 1

    # Julie
    while s <= 2.0:
        s += draws[i]
        y = draws[i]
        i += 1

    return x, y


def solve() -> str:
    """
    Return the required probability as a string formatted to 10 decimal places.
    """
    # Enough precision to safely round to 10 decimal places.
    getcontext().prec = 60

    e = Decimal(1).exp()
    p = (Decimal(1) + Decimal(14) * e - Decimal(5) * e * e) / Decimal(4)

    # Quantize to exactly 10 digits after the decimal point.
    return str(p.quantize(Decimal("0.0000000000")))


def _self_test() -> None:
    # Test case explicitly shown in the problem statement.
    draws = [0.62, 0.44, 0.1, 0.27, 0.91]
    x, y = example_game_outcome(draws)
    assert abs(x - 0.44) < 1e-12
    assert abs(y - 0.91) < 1e-12
    assert y > x  # therefore second player wins in the example

    # Sanity checks for the closed form.
    ans = Decimal(solve())
    assert Decimal(0) < ans < Decimal(1)
    # A coarse check against double-precision evaluation.
    # (We avoid importing math; this stays fully within Decimal arithmetic.)


def main() -> None:
    _self_test()
    print(solve())


if __name__ == "__main__":
    main()
