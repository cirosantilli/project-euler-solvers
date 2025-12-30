#!/usr/bin/env python3
"""Project Euler 308: An amazing prime-generating automaton.

We need the number of FRACTRAN iterations until Conway's PRIMEGAME program
(first power-of-2 outputs are 2^2, 2^3, 2^5, ...) reaches 2^(10001st prime).

This implementation avoids simulating the huge integer state. Instead, it uses
an exact closed-form for the number of FRACTRAN iterations needed for each
"outer" step N (which corresponds to checking whether N is prime).

The final answer for the original Euler problem (n=10001) is printed.

If you pass an integer on stdin, it will compute the answer for that n instead.
"""

from __future__ import annotations

import math
import sys
from typing import List, Tuple


# Conway's PRIMEGAME program (Euler 308) as integer numerator/denominator pairs.
FRACTIONS: List[Tuple[int, int]] = [
    (17, 91),
    (78, 85),
    (19, 51),
    (23, 38),
    (29, 33),
    (77, 29),
    (95, 23),
    (77, 19),
    (1, 17),
    (11, 13),
    (13, 11),
    (15, 2),
    (1, 7),
    (55, 1),
]


def _fractran_iterate(seed: int, steps: int) -> List[int]:
    """Return the first `steps` outputs of the FRACTRAN program from `seed`.

    Used only for small self-tests against the example values in the statement.
    """
    x = seed
    out: List[int] = []
    for _ in range(steps):
        for num, den in FRACTIONS:
            if x % den == 0:
                x = (x // den) * num
                out.append(x)
                break
        else:
            raise RuntimeError("FRACTRAN halted unexpectedly")
    return out


def _nth_prime(n: int) -> int:
    """Return the nth prime (1-indexed) using a sieve."""
    if n < 1:
        raise ValueError("n must be >= 1")

    # Upper bound for nth prime: n(log n + log log n) + O(n)
    # Good enough for n=10001.
    if n < 6:
        limit = 15
    else:
        limit = int(n * (math.log(n) + math.log(math.log(n)))) + 10

    while True:
        sieve = bytearray(b"\x01") * (limit + 1)
        sieve[0:2] = b"\x00\x00"
        r = int(limit**0.5)
        for p in range(2, r + 1):
            if sieve[p]:
                start = p * p
                sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)

        count = 0
        for i in range(2, limit + 1):
            if sieve[i]:
                count += 1
                if count == n:
                    return i

        limit *= 2


def _largest_proper_divisors(limit: int) -> List[int]:
    """Compute largest proper divisor b(n) for all 1 <= n <= limit.

    b(1) = 1.
    For prime n, b(n) = 1.
    For composite n, b(n) = n / smallest_prime_factor(n).
    """
    if limit < 1:
        return [0]

    spf = [0] * (limit + 1)
    for i in range(2, limit + 1):
        if spf[i] == 0:
            spf[i] = i
            if i * i <= limit:
                for j in range(i * i, limit + 1, i):
                    if spf[j] == 0:
                        spf[j] = i

    spf[1] = 1

    lpd = [1] * (limit + 1)
    for n in range(2, limit + 1):
        p = spf[n]
        lpd[n] = 1 if p == n else n // p
    return lpd


def _sum_floor_div_range(n: int, lo: int, hi: int) -> int:
    """Compute sum_{d=lo..hi} floor(n/d) in O(sqrt(n)) time."""
    s = 0
    d = lo
    while d <= hi:
        q = n // d
        last = n // q
        if last > hi:
            last = hi
        s += q * (last - d + 1)
        d = last + 1
    return s


def steps_until_power_of_two_exponent(exponent: int) -> int:
    """Number of FRACTRAN iterations until the boundary state reaches 2^exponent.

    The program repeatedly reaches boundary states of the form:
        2^N * 7^(b(N)-1)
    where b(N) is the largest proper divisor of N (or 1 if N is prime).

    Each boundary transition N-1 -> N has a closed form step count that depends
    on N, b(N), and the previous b(N-1). Summing those costs for N=2..exponent
    yields the exact number of FRACTRAN iterations until the boundary for N.

    For prime exponent, the 7-exponent is 0, so the boundary is exactly 2^exponent.
    """
    if exponent < 1:
        raise ValueError("exponent must be >= 1")
    if exponent == 1:
        return 0  # seed = 2 = 2^1

    lpd = _largest_proper_divisors(exponent)

    total = 0
    prev_b = 1  # b(1)
    for N in range(2, exponent + 1):
        b = lpd[N]
        # Core term (matches the well-known analysis of Conway's primegame):
        #   N-1 + (6N+2)(N-b) + 2*sum_{d=b..N-1} floor(N/d)
        # In the original Euler 308 fraction list (which includes 1/7), there is
        # an additional countdown of the previous 7-exponent, which contributes
        # (prev_b - 1) steps.
        floor_sum = _sum_floor_div_range(N, b, N - 1)
        cost = (N - 1) + (6 * N + 2) * (N - b) + 2 * floor_sum + (prev_b - 1)
        total += cost
        prev_b = b

    return total


def solve(n: int = 10001) -> int:
    """Return the Euler 308 answer for a given n (using the same FRACTRAN program)."""
    p = _nth_prime(n)
    return steps_until_power_of_two_exponent(p)


def _self_test() -> None:
    # Tests based on the example values in the problem statement.
    # (The statement shows a few scattered terms from the generated sequence.)

    seq20 = _fractran_iterate(2, 20)
    assert seq20[:6] == [15, 825, 725, 1925, 2275, 425]
    # ... , 68, 4, 30, ...
    assert seq20[17:20] == [68, 4, 30]

    seq70 = _fractran_iterate(2, 70)
    # ... , 136, 8, 60, ...
    assert seq70[67:70] == [136, 8, 60]

    seq282 = _fractran_iterate(2, 282)
    # ... , 544, 32, 240, ...
    assert seq282[279:282] == [544, 32, 240]

    # Cross-check a few known boundary counts for the original fraction list.
    assert steps_until_power_of_two_exponent(2) == 19
    assert steps_until_power_of_two_exponent(3) == 69
    assert steps_until_power_of_two_exponent(5) == 281
    assert steps_until_power_of_two_exponent(7) == 710


def main() -> None:
    data = sys.stdin.read().strip()
    n = int(data) if data else 10001
    print(solve(n))


if __name__ == "__main__":
    _self_test()
    main()
