"""Project Euler 322: Binomial Coefficients Divisible by 10.

Let T(m, n) be the number of binomial coefficients iCn that are divisible by 10
for n <= i < m.

We use Lucas' theorem to count when iCn is NOT divisible by a prime p.
Then apply inclusion–exclusion for p=2 and p=5.

The intersection (not divisible by 2 AND not divisible by 5) is computed
efficiently by enumerating the (small) set of valid base-5 low parts and using
modular inverses modulo a power of two.
"""

from __future__ import annotations

from functools import lru_cache


def digits_base(x: int, base: int) -> list[int]:
    """Return digits of x in given base, least-significant first."""
    if x < 0:
        raise ValueError("x must be non-negative")
    if base <= 1:
        raise ValueError("base must be >= 2")
    if x == 0:
        return [0]
    out: list[int] = []
    while x:
        out.append(x % base)
        x //= base
    return out


def count_supermask_lt(limit: int, mask: int) -> int:
    """Count integers x with 0 <= x < limit and (x & mask) == mask."""
    if limit <= 0:
        return 0

    bits = limit.bit_length()
    # Digit-DP over bits with a "tight" (=equal-prefix) and "loose" (<prefix) state.
    dp_tight = 1
    dp_loose = 0
    for p in range(bits - 1, -1, -1):
        lim_bit = (limit >> p) & 1
        forced = (mask >> p) & 1
        new_tight = 0
        new_loose = 0

        # Already < limit: lim_bit irrelevant.
        if dp_loose:
            if forced:
                new_loose += dp_loose
            else:
                new_loose += dp_loose * 2

        # Still equal to limit's prefix.
        if dp_tight:
            if forced:
                # Must set 1.
                if lim_bit == 1:
                    new_tight += dp_tight
            else:
                # Can choose 0/1 within the limit.
                if lim_bit == 0:
                    new_tight += dp_tight  # choose 0
                else:
                    new_loose += dp_tight  # choose 0, becomes loose
                    new_tight += dp_tight  # choose 1, stays tight

        dp_tight, dp_loose = new_tight, new_loose

    # dp_tight corresponds to x == limit, which we must exclude.
    return dp_loose


def count_lucas_not_divisible_lt(limit: int, n: int, base: int) -> int:
    """Count i with 0 <= i < limit and iCn is NOT divisible by prime=base.

    For prime p, Lucas' theorem implies iCn (mod p) != 0 iff each base-p digit
    of i is >= the corresponding base-p digit of n.
    """
    if limit <= 0:
        return 0

    upper = limit - 1  # convert strict < limit into <= upper
    lim_digits = digits_base(upper, base)
    n_digits = digits_base(n, base)
    L = max(len(lim_digits), len(n_digits))
    lim_digits += [0] * (L - len(lim_digits))
    n_digits += [0] * (L - len(n_digits))
    lim_msb = lim_digits[::-1]
    n_msb = n_digits[::-1]

    @lru_cache(None)
    def dp(pos: int, tight: bool) -> int:
        if pos == L:
            return 1
        limd = lim_msb[pos]
        mind = n_msb[pos]
        maxd = limd if tight else base - 1
        total = 0
        for d in range(mind, maxd + 1):
            total += dp(pos + 1, tight and d == limd)
        return total

    return dp(0, True)


def generate_lows_base5(n: int) -> tuple[list[int], int]:
    """Enumerate all 'low parts' low < 5^L whose base-5 digits satisfy low_d >= n_d.

    L is the number of base-5 digits of n (no leading zeros). Returns (lows, B)
    where B = 5^L.
    """
    n_digits = digits_base(n, 5)  # lsb
    lows = [0]
    pow5 = 1
    for dmin in n_digits:
        new: list[int] = []
        for low in lows:
            for d in range(dmin, 5):
                new.append(low + d * pow5)
        lows = new
        pow5 *= 5
    return lows, pow5


def count_not_divisible_by_10_lt(m: int, n: int) -> int:
    """Count i with 0 <= i < m such that iCn is coprime to 10.

    Equivalent to: iCn not divisible by 2 AND not divisible by 5.
    """
    if m <= 0:
        return 0

    lows, B = generate_lows_base5(n)

    # i = low + B*h, with low fixed by the constrained base-5 digits.
    max_h = (m - 1) // B
    k = max_h.bit_length() or 1  # choose 2^k > max_h (or 2^1 if max_h=0)
    mod = 1 << k
    invB = pow(B % mod, -1, mod)  # B is odd -> invertible modulo 2^k

    required_low = n & (mod - 1)
    free_positions = [b for b in range(k) if ((required_low >> b) & 1) == 0]
    # Enumerate residues i_mod (mod 2^k) whose required bits are set.
    i_mods: list[int] = []
    for subset in range(1 << len(free_positions)):
        val = required_low
        for j, b in enumerate(free_positions):
            if (subset >> j) & 1:
                val |= 1 << b
        i_mods.append(val)

    out = 0
    for low in lows:
        if low >= m:
            continue
        h_max_for_low = (m - 1 - low) // B
        if h_max_for_low < 0:
            continue

        low_mod = low & (mod - 1)
        for i_mod in i_mods:
            h = ((i_mod - low_mod) * invB) & (mod - 1)
            if h > h_max_for_low:
                continue
            i = low + B * h
            if i < m and (i & n) == n:
                out += 1

    return out


def T(m: int, n: int) -> int:
    """Compute T(m, n) as defined in the problem."""
    if m <= n:
        return 0

    total = m - n
    not2 = count_supermask_lt(m, n)
    not5 = count_lucas_not_divisible_lt(m, n, 5)
    not10 = count_not_divisible_by_10_lt(m, n)
    return total - not2 - not5 + not10


def main() -> None:
    # Given example in the problem statement.
    assert T(10**9, 10**7 - 10) == 989_697_000

    print(T(10**18, 10**12 - 10))


if __name__ == "__main__":
    main()
