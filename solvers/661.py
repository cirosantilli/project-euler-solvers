#!/usr/bin/env python3
"""Project Euler 661: A Long Chess Match

We need H(50) where
  H(n) = sum_{k=3..n} E_A( 1/sqrt(k+3), 1/sqrt(k+3) + 1/k^2, 1/k^3 )

E_A(pA,pB,p) is the expected number of games after which A is leading,
when after each game a biased coin ends the match with probability p.

This solution derives a closed form for E_A by solving a killed
birth-death Markov chain via a linear recurrence.

No external libraries are used.
"""

import math


def expected_times_a_leading(p_a: float, p_b: float, p_stop: float) -> float:
    """Compute E_A(p_a, p_b, p_stop)."""
    # q: probability the match continues after a game
    q = 1.0 - p_stop

    # The score difference D evolves by +1 (A win), -1 (B win), 0 (draw).
    # After each game we record whether D>0, then stop with prob p_stop.
    #
    # The value function V(d) = expected total future "A is leading" counts
    # starting from score difference d *before* playing the next game.
    # V satisfies a second-order linear recurrence with a boundary layer at
    # d in {0,1}. Solving it yields V(0) in terms of the roots of
    #   a r^2 - c r + b = 0
    # where a=q*p_a, b=q*p_b, c=p_stop + q*(p_a+p_b).

    a = q * p_a
    b = q * p_b
    c = p_stop + q * (p_a + p_b)

    disc = c * c - 4.0 * a * b
    # Numerical guard: disc should be >= 0, but tiny negatives can appear.
    if disc < 0.0 and disc > -1e-15:
        disc = 0.0
    s = math.sqrt(disc)

    # Use a stable root computation:
    # r2 is the larger root, r1 the smaller; r1*r2 = b/a.
    r2 = (c + s) / (2.0 * a)
    r1 = b / (a * r2)

    # Closed form for V(0) (= E_A):
    # V0 = (1/p + 1/q) * (1 - r1) / (r2 - r1)
    return (1.0 / p_stop + 1.0 / q) * (1.0 - r1) / (r2 - r1)


def H(n: int) -> float:
    total = 0.0
    for k in range(3, n + 1):
        p_a = 1.0 / math.sqrt(k + 3.0)
        p_b = p_a + 1.0 / (k * k)
        p_stop = 1.0 / (k**3)
        total += expected_times_a_leading(p_a, p_b, p_stop)
    return total


def _self_test() -> None:
    # Test values from the problem statement
    v1 = expected_times_a_leading(0.25, 0.25, 0.5)
    assert round(v1, 6) == 0.585786

    v2 = expected_times_a_leading(0.47, 0.48, 0.001)
    assert round(v2, 6) == 377.471736

    h3 = H(3)
    assert round(h3, 4) == 6.8345


def main() -> None:
    _self_test()
    ans = H(50)
    print(f"{ans:.4f}")


if __name__ == "__main__":
    main()
