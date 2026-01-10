#!/usr/bin/env python3
"""
Project Euler 599: Distinct Colourings of a Rubik's Cube (2x2x2)

We count essentially distinct colourings of the 24 facelets using n colours,
under the action of the 2x2x2 cube move group.

Key facts:
- A 2x2x2 cube has 8 corner cubies, each with 3 stickers => 24 facelets.
- The move group on corners is S8 (all permutations) with corner twists in Z3,
  constrained by total twist sum ≡ 0 mod 3.
  => group size = 8! * 3^7.

Using Burnside's lemma:
#orbits = (1/|G|) * sum_{g in G} n^{c(g)},
where c(g) is the number of cycles in the permutation induced on 24 stickers.

We exploit wreath-product structure:
Each corner permutation cycle (length k) contributes:
- 3 sticker-cycles if the sum of twists on that corner cycle is 0 mod 3
- 1 sticker-cycle otherwise
Thus for a corner permutation with m cycles and z cycles with twist-sum 0:
c(g) = (m - z)*1 + z*3 = m + 2z

Then we count how many corner permutations have exactly m cycles:
= unsigned Stirling number of the first kind c(8,m).

For fixed m, we count how many m-tuples over {0,1,2} with total sum 0 mod 3
have exactly z zeros. This reduces to counting r-tuples over {1,2} summing to 0.
"""

from math import factorial, comb


def unsigned_stirling_first_kind(n: int):
    """Return table c(n,k) for unsigned Stirling numbers of the first kind."""
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    dp[0][0] = 1
    for i in range(1, n + 1):
        for k in range(1, i + 1):
            dp[i][k] = dp[i - 1][k - 1] + (i - 1) * dp[i - 1][k]
    return dp[n]


def count_sequences_12_sum0(max_len: int):
    """
    For r = 0..max_len, compute B(r) where
    B(r) = number of r-tuples in {1,2}^r with sum ≡ 0 (mod 3).
    """
    dp = [[0, 0, 0] for _ in range(max_len + 1)]
    dp[0][0] = 1
    for r in range(max_len):
        for s in range(3):
            dp[r + 1][(s + 1) % 3] += dp[r][s]
            dp[r + 1][(s + 2) % 3] += dp[r][s]
    return [dp[r][0] for r in range(max_len + 1)]


def distinct_colourings(n: int) -> int:
    """
    Return number of essentially distinct colourings with n colours.
    """
    # Corner permutations: S8
    # c8[m] = number of permutations on 8 elements with exactly m cycles
    c8 = unsigned_stirling_first_kind(8)

    # B(r) counts sequences length r over {1,2} with sum ≡ 0 mod 3
    B = count_sequences_12_sum0(8)

    numerator = 0
    for m in range(1, 9):
        # For a permutation with m corner-cycles:
        # each corner-cycle has 3^{len-1} twist assignments yielding any cycle-sum
        # => factor over all cycles: 3^{8-m}
        factor = 3 ** (8 - m)

        # Count m-tuples of cycle sums in Z3 with total sum 0,
        # grouped by z = number of zero entries.
        term_m = 0
        for z in range(m + 1):
            r = m - z  # number of nonzero entries (1 or 2)
            # choose which z are zeros, remaining r are in {1,2} with sum 0 mod 3
            count_vectors = comb(m, z) * B[r]
            cycles_on_stickers = m + 2 * z
            term_m += count_vectors * (n**cycles_on_stickers)

        numerator += c8[m] * factor * term_m

    denom = factorial(8) * (3**7)
    assert numerator % denom == 0
    return numerator // denom


def main():
    # Test value from problem statement
    assert distinct_colourings(2) == 183

    # Required answer
    print(distinct_colourings(10))


if __name__ == "__main__":
    main()
