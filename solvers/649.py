#!/usr/bin/env python3
"""
Project Euler 649: Low-Prime Chessboard Nim

Compute the last 9 digits of M(10_000_019, 100).
No external libraries are used.
"""

MOD = 1_000_000_000  # last 9 digits
MOVES = (2, 3, 5, 7)  # allowed step sizes (left/up)


def _mex_table(max_value: int = 4):
    """Precompute mex(mask) for masks over values 0..max_value."""
    size = 1 << (max_value + 1)
    mex = [0] * size
    for mask in range(size):
        m = 0
        # find first zero bit
        while (mask >> m) & 1:
            m += 1
        mex[mask] = m
    return mex


_MEX = _mex_table(4)


def heap_grundy_frequencies(n: int):
    """
    For the 1D subtraction game on positions 0..n-1 with moves -2,-3,-5,-7,
    return freq[g] = count of positions with Grundy number g.

    Grundy values are <= 4 because each position has at most 4 options.
    """
    if n <= 0:
        return [0] * 5

    ring = [0] * 8  # circular buffer for last 8 Grundy values (need up to t-7)
    freq = [0] * 5

    # Handle t = 0..6 with boundary checks
    limit = min(n, 7)
    for t in range(limit):
        mask = 0
        if t >= 2:
            mask |= 1 << ring[(t - 2) & 7]
        if t >= 3:
            mask |= 1 << ring[(t - 3) & 7]
        if t >= 5:
            mask |= 1 << ring[(t - 5) & 7]
        if t >= 7:
            mask |= 1 << ring[(t - 7) & 7]
        g = _MEX[mask]
        ring[t & 7] = g
        freq[g] += 1

    # From t >= 7 all four moves are available (no boundary checks)
    for t in range(7, n):
        mask = (
            (1 << ring[(t - 2) & 7])
            | (1 << ring[(t - 3) & 7])
            | (1 << ring[(t - 5) & 7])
            | (1 << ring[(t - 7) & 7])
        )
        g = _MEX[mask]
        ring[t & 7] = g
        freq[g] += 1

    return freq


def board_nimber_counts(n: int):
    """
    Count how many squares (x,y) in an n x n board have nimber k for a single coin.
    With only left/up moves, the coin game is the disjunctive sum of two 1D games,
    so SG(x,y) = g(x) XOR g(y).
    Returns a list a[0..7] where sum(a) = n^2.
    """
    f = heap_grundy_frequencies(n)  # f[0..4]
    a = [0] * 8
    for i, fi in enumerate(f):
        if fi:
            for j, fj in enumerate(f):
                if fj:
                    a[i ^ j] += fi * fj
    return a


def xor_convolve(u, v, mod: int):
    """XOR convolution of length-8 vectors under modulus."""
    w = [0] * 8
    for i, ui in enumerate(u):
        if ui:
            for j, vj in enumerate(v):
                if vj:
                    w[i ^ j] = (w[i ^ j] + ui * vj) % mod
    return w


def xor_power(base, exp: int, mod: int):
    """
    Compute the exp-fold XOR-convolution power of 'base' (length 8),
    i.e. distribution of XOR of exp i.i.d. draws with weights base.
    """
    res = [0] * 8
    res[0] = 1  # identity element for XOR convolution
    while exp:
        if exp & 1:
            res = xor_convolve(res, base, mod)
        base = xor_convolve(base, base, mod)
        exp >>= 1
    return res


def M_mod(n: int, c: int, mod: int = MOD) -> int:
    """
    Return M(n,c) modulo 'mod', where M is the number of starting arrangements
    in which the first player has a winning strategy.
    """
    # Distribution of nimbers for a single coin position
    a = board_nimber_counts(n)
    a_mod = [x % mod for x in a]

    # Losing arrangements are those with XOR of coin nimbers == 0
    dist = xor_power(a_mod, c, mod)
    losing = dist[0]

    # Total arrangements: (n^2)^c
    total = pow((n * n) % mod, c, mod)

    return (total - losing) % mod


def _self_test():
    # Test values from the problem statement
    assert M_mod(3, 1) == 4
    assert M_mod(3, 2) == 40
    assert M_mod(9, 3) == 450304


def main():
    _self_test()
    ans = M_mod(10_000_019, 100)
    print(f"{ans:09d}")  # last 9 digits (zero-padded)


if __name__ == "__main__":
    main()
