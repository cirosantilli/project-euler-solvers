#!/usr/bin/env python3
"""
Project Euler 383: Divisibility comparison between factorials

We need:
T5(n) = #{ i : 1 <= i <= n and v5((2i-1)!) < 2*v5(i!) }

Key identity (Legendre + base-5 digit sums):
v5(m!) = (m - s5(m)) / 4
So the inequality becomes:
s5(2i-1) >= 2*s5(i)

We count i <= n satisfying this via a digit-DP in base 5.
The main subtlety is that digits of (2i-1) depend on carries/borrows
propagating from the *least* significant side, while the usual <= n
constraint is easiest from the most significant side. We solve this by
running the DP "backwards": from the most significant digit to the least,
using precomputed *reverse* transitions of the carry/borrow automaton.

No external libraries are used (only Python stdlib).
"""

from functools import lru_cache


def base5_digits_msd(n: int) -> list[int]:
    """Return base-5 digits of n as a list [MSD..LSD], with n>=0."""
    if n <= 0:
        return [0]
    digs = []
    while n:
        digs.append(n % 5)
        n //= 5
    return digs[::-1]


def build_reverse_transitions():
    """
    Forward processing (from LSD to MSD) uses state (carry, borrow) where:
      carry in {0,1} comes from doubling,
      borrow in {0,1} comes from subtracting 1 (initially borrow=1).
    For a digit d in {0..4}:
      raw0 = 2*d + carry - borrow
      if raw0 < 0: raw = raw0 + 5, borrow_out = 1 else borrow_out = 0
      e = raw % 5
      carry_out = raw // 5
    We precompute reverse transitions:
      given (carry_out, borrow_out, d) -> possible (carry_in, borrow_in, e)
    """
    rev = {}
    for carry_in in (0, 1):
        for borrow_in in (0, 1):
            for d in range(5):
                raw0 = 2 * d + carry_in - borrow_in
                if raw0 < 0:
                    raw = raw0 + 5
                    borrow_out = 1
                else:
                    raw = raw0
                    borrow_out = 0
                e = raw % 5
                carry_out = raw // 5
                key = (carry_out, borrow_out, d)
                rev.setdefault(key, []).append((carry_in, borrow_in, e))
    return rev


REV = build_reverse_transitions()


def T5(n: int) -> int:
    """Compute T5(n) for n >= 0."""
    digits = base5_digits_msd(n)
    L = len(digits)

    @lru_cache(maxsize=None)
    def dfs(pos: int, tight: int, carry_next: int, borrow_next: int, delta: int) -> int:
        """
        We assign digits of i from MSD to LSD (pos=0..L-1).

        However, the (2i-1) carry/borrow process naturally runs from LSD->MSD.
        So we run the automaton backwards:
          We keep the state *after* processing all lower digits:
            (carry_next, borrow_next) == (carry_{k+1}, borrow_{k+1})
          and at this position choose digit d and step to the previous state
            (carry_prev, borrow_prev) == (carry_k, borrow_k).

        delta tracks:  delta = s5(2i-1) - 2*s5(i) accumulated so far (including
        the final extra carry digit; see initialization below).
        """
        if pos == L:
            # After processing all digits we must land at the initial state (carry=0, borrow=1).
            return 1 if (carry_next == 0 and borrow_next == 1 and delta >= 0) else 0

        limit = digits[pos] if tight else 4
        total = 0

        for d in range(limit + 1):
            tight2 = 1 if (tight and d == limit) else 0
            key = (carry_next, borrow_next, d)
            if key not in REV:
                continue
            for carry_prev, borrow_prev, e in REV[key]:
                # This digit contributes e - 2*d to delta.
                total += dfs(
                    pos + 1, tight2, carry_prev, borrow_prev, delta + e - 2 * d
                )

        return total

    # Final borrow must be 0 (2i-1 is non-negative for i>=1).
    # Final carry (extra digit beyond our fixed length) can be 0 or 1.
    # That extra digit contributes +carry_final to s5(2i-1), hence delta starts at carry_final.
    ans = 0
    for carry_final in (0, 1):
        ans += dfs(0, 1, carry_final, 0, carry_final)
    return ans


def solve() -> int:
    # Test values given in the problem statement.
    assert T5(10**3) == 68
    assert T5(10**9) == 2408210

    return T5(10**18)


if __name__ == "__main__":
    print(solve())
