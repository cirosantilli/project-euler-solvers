#!/usr/bin/env python3
"""
Project Euler 588 - Quintinomial Coefficients

We need:
  Q(k) = number of odd coefficients in (1 + x + x^2 + x^3 + x^4)^k
and output:
  sum_{m=1..18} Q(10^m)

Key idea: work mod 2 (odd/even), use Frobenius in GF(2) and a small carry automaton.
"""


def _build_transitions(active: bool):
    """
    Build transitions for one bit-position.

    State is a 4-bit mask representing a parity vector v over carries c=0..3:
      bit c of state == v[c] (mod 2), i.e. odd number of ways to reach carry c
      after processing the lower bits of the exponent n.

    Input symbol is the exponent bit n_i (0/1).

    active=False: digit at this position is forced to d=0 (because k_i=0)
    active=True : digit can be any d in {0,1,2,3,4} (because k_i=1)

    For each carry c and chosen digit d:
      s = c + d
      output bit is s mod 2
      next carry is floor(s/2)

    Because everything is mod 2, we only care whether the number of transitions is odd/even.
    """
    digits = range(5) if active else (0,)
    # trans[bit][state] -> next_state
    trans = [[0] * 16 for _ in range(2)]
    for bit in (0, 1):
        for state in range(16):
            next_state = 0
            for c in range(4):
                if (state >> c) & 1:
                    for d in digits:
                        s = c + d
                        if (s & 1) == bit:
                            nc = s >> 1  # 0..3
                            next_state ^= 1 << nc  # toggle in GF(2)
            trans[bit][state] = next_state
    return trans


# Precompute the only two transition types we need.
_TRANS_ACTIVE = _build_transitions(True)
_TRANS_INACTIVE = _build_transitions(False)


def Q(k: int) -> int:
    """
    Count odd coefficients in (1+x+x^2+x^3+x^4)^k.

    We count all exponents n (in binary, padded to a fixed length L) such that
    the parity of the coefficient of x^n is 1.

    DP over exponent bits n_i (each can be 0 or 1):
      dp[state] = number of prefixes yielding this carry-parity vector 'state'.

    L only needs to cover all bit-positions where k may contribute (plus a small carry buffer).
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    # Enough bits to include the highest possible contribution and to settle any carry.
    L = k.bit_length() + 3

    dp = [0] * 16
    dp[1] = 1  # v = (1,0,0,0): one way, carry 0 before reading any bits

    for i in range(L):
        trans = _TRANS_ACTIVE if ((k >> i) & 1) else _TRANS_INACTIVE
        ndp = [0] * 16
        for state, cnt in enumerate(dp):
            if cnt:
                ndp[trans[0][state]] += cnt
                ndp[trans[1][state]] += cnt
        dp = ndp

    # Coefficient parity for an exponent n is v_final[0], i.e. bit0 of 'state'.
    return sum(cnt for state, cnt in enumerate(dp) if (state & 1))


def solve() -> int:
    # Test values from the problem statement.
    assert Q(3) == 7
    assert Q(10) == 17
    assert Q(100) == 35

    total = 0
    k = 10
    for _ in range(18):
        total += Q(k)
        k *= 10
    return total


if __name__ == "__main__":
    print(solve())
