#!/usr/bin/env python3
"""
Project Euler 629 - Scatterstone Nim

We count winning positions for Alice in a Nim variant:
- A position is an unordered multiset of piles summing to n (integer partition).
- A move selects a pile s>=2 and splits it into p non-empty piles, with 2<=p<=k.
- Normal play: if you cannot move, you lose.

For fixed k, the game is impartial:
- Each pile size s has a Sprague-Grundy value G_k(s).
- A position is losing iff XOR of all pile SG values is 0.

Let P(n) be the number of integer partitions of n (all possible starting positions).
Let L(n,k) be the number of losing positions (XOR = 0).
Then f(n,k) = P(n) - L(n,k).

Key observation (validated by samples):
- For k >= 4, G_k(s) = s-1 for all s.
  Thus f(n,k) is constant for all k>=4.
So:
  g(n) = f(n,2) + f(n,3) + (n-3)*f(n,4)   for n>=4.

We compute:
- G_2(s) easily: 1 if s even else 0.
- G_3(s) by mex over splits into 2 or 3 piles.
- G_4(s) by formula: s-1.

To count losing positions L(n,k), we count partitions of n with XOR 0.
We do a partition DP over pile sizes, but multiplicities only matter by parity:
Any multiplicity m is (2r) or (2r+1), i.e. "pairs" + optional single.

Factor for a part size i with nimber g:
  (1 + x^i*T) / (1 - x^(2i))
Where T means XOR with g.

So we update DP in two steps:
1) unlimited coin of size 2i (no XOR change)
2) 0/1 coin of size i (XOR with g)

All arithmetic is mod 1e9+7.
"""

MOD = 1_000_000_007


def partition_numbers_up_to(N, mod=MOD):
    """Return list p[0..N] where p[n] = number of integer partitions of n (mod)."""
    p = [0] * (N + 1)
    p[0] = 1
    for part in range(1, N + 1):
        for s in range(part, N + 1):
            p[s] += p[s - part]
            if p[s] >= mod:
                p[s] -= mod
    return p


def grundy_k2(N):
    """For k=2, a heap has nimber 1 iff its size is even, else 0."""
    g = [0] * (N + 1)
    for s in range(2, N + 1):
        g[s] = 1 if (s % 2 == 0) else 0
    return g


def grundy_k3(N):
    """
    Compute Grundy numbers for k=3:
    reachable moves = splits into 2 or 3 non-empty piles.
    """
    g = [0] * (N + 1)
    for n in range(2, N + 1):
        seen = [False] * 256  # safe for N<=200; max mex observed is 101

        # 2-part splits: a + (n-a), with a <= n-a
        for a in range(1, n // 2 + 1):
            seen[g[a] ^ g[n - a]] = True

        # 3-part splits: a <= b <= c, a+b+c = n
        for a in range(1, n // 3 + 1):
            max_b = (n - a) // 2
            for b in range(a, max_b + 1):
                c = n - a - b
                if b <= c:
                    seen[g[a] ^ g[b] ^ g[c]] = True

        mex = 0
        while mex < len(seen) and seen[mex]:
            mex += 1
        g[n] = mex
    return g


def grundy_k4plus(N):
    """For k>=4, nimber is s-1."""
    return [max(0, s - 1) for s in range(N + 1)]


def next_power_of_two(x):
    """Return smallest power of two >= x."""
    p = 1
    while p < x:
        p <<= 1
    return p


def count_losing_partitions(n, grundy, mod=MOD):
    """
    Count partitions of n whose XOR of pile grundy values equals 0.
    Uses parity decomposition per pile size i:
      multiplicity = (pairs of size 2i) + optional single i.
    """
    max_g = 0
    for s in range(1, n + 1):
        if grundy[s] > max_g:
            max_g = grundy[s]
    width = next_power_of_two(max_g + 1)
    if width < 2:
        width = 2

    dp = [[0] * width for _ in range(n + 1)]
    dp[0][0] = 1

    for size in range(1, n + 1):
        g = grundy[size]
        pair = 2 * size

        # Step 1: unlimited pairs (coin size 2*size, XOR unchanged)
        if pair <= n:
            for s in range(pair, n + 1):
                src = dp[s - pair]
                dst = dp[s]
                for x, val in enumerate(src):
                    if val:
                        nv = dst[x] + val
                        if nv >= mod:
                            nv -= mod
                        dst[x] = nv

        # Step 2: optional single (0/1 coin size size, XOR with g)
        for s in range(n, size - 1, -1):
            src = dp[s - size]
            dst = dp[s]
            if g == 0:
                for x, val in enumerate(src):
                    if val:
                        nv = dst[x] + val
                        if nv >= mod:
                            nv -= mod
                        dst[x] = nv
            else:
                for x, val in enumerate(src):
                    if val:
                        j = x ^ g
                        nv = dst[j] + val
                        if nv >= mod:
                            nv -= mod
                        dst[j] = nv

    return dp[n][0]


def f_value(n, k, partitions, g2, g3, g4, mod=MOD):
    """Compute f(n,k) mod mod."""
    total = partitions[n]
    if k == 2:
        losing = count_losing_partitions(n, g2, mod)
    elif k == 3:
        losing = count_losing_partitions(n, g3, mod)
    else:
        losing = count_losing_partitions(n, g4, mod)
    return (total - losing) % mod


def g_value(n, partitions, g2, g3, g4, mod=MOD):
    """Compute g(n)=sum_{k=2..n} f(n,k) mod mod."""
    if n < 2:
        return 0
    f2 = f_value(n, 2, partitions, g2, g3, g4, mod)
    if n == 2:
        return f2
    f3 = f_value(n, 3, partitions, g2, g3, g4, mod)
    if n == 3:
        return (f2 + f3) % mod
    f4 = f_value(n, 4, partitions, g2, g3, g4, mod)
    return (f2 + f3 + (n - 3) * f4) % mod


def main():
    N = 200
    partitions = partition_numbers_up_to(N, MOD)
    g2 = grundy_k2(N)
    g3 = grundy_k3(N)
    g4 = grundy_k4plus(N)

    # Asserts from problem statement
    assert f_value(5, 2, partitions, g2, g3, g4) == 3
    assert f_value(5, 3, partitions, g2, g3, g4) == 5
    assert g_value(7, partitions, g2, g3, g4) == 66
    assert g_value(10, partitions, g2, g3, g4) == 291

    print(g_value(200, partitions, g2, g3, g4))


if __name__ == "__main__":
    main()
