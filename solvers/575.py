#!/usr/bin/env python3
"""
Project Euler 575 - Wandering Robots

We compute the long-run (stationary) probability that the robot is in a room
whose *index* is a perfect square on an n x n grid, where the robot was programmed
by a fair coin toss to use one of two movement rules.

No external libraries are used (stdlib only).
"""

from math import gcd


def count_square_cells_by_class(n: int):
    """
    Returns (interior, edge_noncorner, corner) counts among the n perfect squares:
    1^2, 2^2, ..., n^2 mapped onto an n x n grid numbered row-major from 1..n^2.
    """
    interior = edge = corner = 0
    for s in range(1, n + 1):
        x = s * s  # room number (1-indexed)
        r = (x - 1) // n + 1
        c = (x - 1) % n + 1

        is_top_or_bottom = r == 1 or r == n
        is_left_or_right = c == 1 or c == n

        if is_top_or_bottom and is_left_or_right:
            corner += 1
        elif is_top_or_bottom or is_left_or_right:
            edge += 1
        else:
            interior += 1
    return interior, edge, corner


def reduced_fraction(num: int, den: int):
    g = gcd(num, den)
    return num // g, den // g


def add_fractions(a_num: int, a_den: int, b_num: int, b_den: int):
    num = a_num * b_den + b_num * a_den
    den = a_den * b_den
    return reduced_fraction(num, den)


def mul_fraction_by_int(num: int, den: int, k: int):
    num *= k
    return reduced_fraction(num, den)


def stationary_prob_square(n: int, rule: int):
    """
    rule=1 corresponds to:
      options = {stay} U {adjacent rooms}, each chosen with equal probability.
      Stationary weights are proportional to (#exits + 1).

    rule=2 corresponds to:
      stay with probability 1/2; otherwise move to a random adjacent room.
      Stationary weights are proportional to (#exits).

    Returns (num, den) reduced.
    """
    if n < 2:
        raise ValueError("n must be >= 2")

    sq_i, sq_e, sq_c = count_square_cells_by_class(n)

    if rule == 1:
        w_i, w_e, w_c = 5, 4, 3  # exits 4/3/2 plus 1
    elif rule == 2:
        w_i, w_e, w_c = 4, 3, 2  # exits 4/3/2
    else:
        raise ValueError("rule must be 1 or 2")

    total_weight = w_i * (n - 2) * (n - 2) + w_e * 4 * (n - 2) + w_c * 4
    square_weight = sq_i * w_i + sq_e * w_e + sq_c * w_c

    return reduced_fraction(square_weight, total_weight)


def average_probability(n: int):
    """Average of the two stationary probabilities (fair coin). Returns (num, den) reduced."""
    p1_num, p1_den = stationary_prob_square(n, 1)
    p2_num, p2_den = stationary_prob_square(n, 2)
    s_num, s_den = add_fractions(p1_num, p1_den, p2_num, p2_den)
    # divide by 2
    return reduced_fraction(s_num, s_den * 2)


def format_fraction(num: int, den: int, dp: int = 12) -> str:
    """
    Formats num/den rounded to dp decimal places (half-up), using integer arithmetic.
    """
    scale = 10**dp
    scaled = num * scale
    q, r = divmod(scaled, den)
    if 2 * r >= den:
        q += 1
    integer_part, frac_part = divmod(q, scale)
    return f"{integer_part}.{frac_part:0{dp}d}"


def solve(n: int = 1000) -> str:
    num, den = average_probability(n)
    return format_fraction(num, den, 12)


def _tests():
    # Given in the problem statement: 5x5 grid -> 0.177976190476 (12 d.p.)
    assert solve(5) == "0.177976190476"

    # Sanity: result should be between 0 and 1, and decrease for large n relative to 5x5.
    n1000 = solve(1000)
    assert n1000.startswith("0.")
    assert float(n1000) < float(solve(5))


def main():
    _tests()
    print(solve(1000))


if __name__ == "__main__":
    main()
