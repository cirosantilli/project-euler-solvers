#!/usr/bin/env python3
"""
Project Euler 396: Weak Goodstein sequence

We need the last 9 digits of:
    S = sum_{1 <= n < 16} G(n)

Where G(n) is the number of non-zero terms in the weak Goodstein sequence
starting from n.

Key facts used (sketched in README):
- Let a(n) be the final base reached (so the sequence value becomes 0 at base a(n)).
  Then G(n) = a(n) - 2.
- a(n) equals a Hardy-hierarchy value H_{alpha(n)}(2), where alpha(n) is the ordinal
  obtained from the binary expansion of n by replacing base 2 with ω.
- For n < 16 we only need one ω^3 term at most.
- H_{ω^2}(x) has a closed form: (x+1)*2^(x+1) - 1.
  Let f(x) = H_{ω^2}(x). Then H_{ω^3}(x) = f applied (x+1) times to x.

The numbers are astronomically large for n >= 8, so we work modulo 10^9 = 2^9 * 5^9,
using:
- the easy behavior of 2^e mod 2^k (it becomes 0 once e >= k),
- Euler reduction on the odd part 5^k,
- a totient-chain to keep the needed residues for exponent reduction,
- CRT to combine mod 2^9 and mod 5^9.
"""

MOD = 1_000_000_000
MOD2 = 1 << 9  # 2^9 = 512
MOD5 = 5**9  # 1953125


# ---------- basic number theory helpers ----------


def _egcd(a: int, b: int):
    """Extended GCD: returns (g, x, y) with ax + by = g = gcd(a,b)."""
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a - q * b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0


def _inv_mod(a: int, m: int) -> int:
    a %= m
    g, x, _ = _egcd(a, m)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % m


def _factor_2_5(n: int):
    """n must be of form 2^a * 5^b. Returns (a,b)."""
    a = b = 0
    tmp = n
    while tmp % 2 == 0:
        tmp //= 2
        a += 1
    while tmp % 5 == 0:
        tmp //= 5
        b += 1
    if tmp != 1:
        raise ValueError("unexpected modulus factorization")
    return a, b


def _phi_2_5(n: int) -> int:
    """Euler's totient for n = 2^a * 5^b."""
    if n == 1:
        return 1
    a, b = _factor_2_5(n)
    # phi(2^a)
    if a == 0:
        phi2 = 1
    elif a == 1:
        phi2 = 1
    else:
        phi2 = 1 << (a - 1)
    # phi(5^b)
    if b == 0:
        phi5 = 1
    else:
        phi5 = 4 * (5 ** (b - 1))
    return phi2 * phi5


def _phi_chain(mod0: int):
    """[mod0, phi(mod0), phi(phi(mod0)), ..., 1] for mod0 = 2^a*5^b."""
    mods = [mod0]
    while mods[-1] != 1:
        mods.append(_phi_2_5(mods[-1]))
    return mods


# ---------- Hardy / weak Goodstein machinery for this problem ----------


def _f2_exact(x: int) -> int:
    """f(x) = H_{ω^2}(x) exactly (only used for tiny x)."""
    e = x + 1
    return (x + 1) * (1 << e) - 1


def _a_exact_upto7(n: int) -> int:
    """
    Exact final base a(n) for n in [0,7], computed from closed forms:
      H_k(x) = x + k
      H_ω(x) = 2x + 1
      H_{ω^2}(x) = (x+1)2^{x+1} - 1
    and alpha(n) from binary digits up to ω^2.

    Returns H_{alpha(n)}(2).
    """
    if not (0 <= n < 8):
        raise ValueError("n out of range for exact shortcut")
    b0 = n & 1
    b1 = (n >> 1) & 1
    b2 = (n >> 2) & 1

    # lower part (ω*b1 + b0)
    x = 2 + b0
    if b1:
        x = 2 * x + 1  # H_ω(x)

    if b2:
        x = _f2_exact(x)  # apply H_{ω^2}
    return x


# Precompute CRT constants for 10^9 = 2^9 * 5^9
_INV_MOD2_MOD5 = _inv_mod(MOD2 % MOD5, MOD5)


def _crt_1e9(r2: int, r5: int) -> int:
    """Combine residues modulo 2^9 and 5^9 into a residue modulo 10^9."""
    t = ((r5 - r2) % MOD5) * _INV_MOD2_MOD5 % MOD5
    return (r2 + MOD2 * t) % MOD


class _ChainInfo:
    __slots__ = ("mod", "a2", "b5", "m2", "m5", "phi5", "inv_m5_mod_m2")

    def __init__(self, mod: int):
        self.mod = mod
        if mod == 1:
            self.a2 = self.b5 = 0
            self.m2 = self.m5 = 1
            self.phi5 = 1
            self.inv_m5_mod_m2 = 0
            return

        a2, b5 = _factor_2_5(mod)
        self.a2, self.b5 = a2, b5
        self.m2 = 1 << a2 if a2 else 1
        self.m5 = 5**b5 if b5 else 1
        self.phi5 = 4 * (5 ** (b5 - 1)) if b5 else 1
        if a2 and b5:
            self.inv_m5_mod_m2 = _inv_mod(self.m5 % self.m2, self.m2)
        else:
            self.inv_m5_mod_m2 = 0


def _build_chain_info(mod0: int):
    mods = _phi_chain(mod0)
    return [_ChainInfo(m) for m in mods]


_CHAIN5 = _build_chain_info(MOD5)


def _pow2_mod_chain_level(info: _ChainInfo, next_res: int, exact_x: int | None) -> int:
    """
    Compute 2^(x+1) mod info.mod, where:
      - x is the current (astronomical) integer,
      - next_res is x mod phi(info.mod) (available from the totient chain),
      - exact_x is x itself only while x is tiny (<= 20), else None.
    """
    m = info.mod
    if m == 1:
        return 0

    # 2-adic part: mod 2^a becomes 0 once exponent >= a.
    if info.a2:
        if exact_x is not None and (exact_x + 1) < info.a2:
            r2 = 1 << (exact_x + 1)
        else:
            r2 = 0
    else:
        r2 = 0

    # 5-adic part: use Euler reduction since gcd(2,5^b)=1.
    if info.b5:
        exp_mod = (next_res % info.phi5 + 1) % info.phi5
        r5 = pow(2, exp_mod, info.m5)
    else:
        r5 = 0

    if info.a2 == 0:
        return r5  # purely 5^b
    if info.b5 == 0:
        return r2  # purely 2^a

    # CRT combine r2 (mod 2^a) and r5 (mod 5^b)
    m2 = info.m2
    mask = m2 - 1
    t = (((r2 - r5) & mask) * info.inv_m5_mod_m2) & mask
    return (r5 + info.m5 * t) % m


def _f2_iter_mod5(x0: int, iters: int) -> int:
    """Compute f applied iters times to x0, modulo 5^9, using the totient chain."""
    residues = [x0 % info.mod for info in _CHAIN5]
    exact_x = x0 if x0 <= 20 else None

    for _ in range(iters):
        new_res = [0] * len(residues)

        # update exact_x (only needed for the tiny first step when exponent < 10)
        if exact_x is not None:
            exact_next = _f2_exact(exact_x)
            exact_x_next = exact_next if exact_next <= 20 else None
        else:
            exact_x_next = None

        for i, info in enumerate(_CHAIN5):
            m = info.mod
            if m == 1:
                new_res[i] = 0
                continue
            next_res = residues[i + 1]  # x mod phi(m)
            p2 = _pow2_mod_chain_level(info, next_res, exact_x)
            new_res[i] = (((residues[i] + 1) % m) * p2 - 1) % m

        residues = new_res
        exact_x = exact_x_next

    return residues[0]


def _f2_iter_mod2(x0: int, iters: int) -> int:
    """Compute f applied iters times to x0, modulo 2^9."""
    mask = MOD2 - 1
    x_mod = x0 & mask
    exact_x = x0 if x0 <= 20 else None

    for _ in range(iters):
        if exact_x is not None and (exact_x + 1) < 9:
            p2 = 1 << (exact_x + 1)
            exact_next = _f2_exact(exact_x)
            exact_x = exact_next if exact_next <= 20 else None
        else:
            p2 = 0
            exact_x = None
        x_mod = (((x_mod + 1) & mask) * p2 - 1) & mask

    return x_mod


def _a_mod(n: int, a0_7: list[int]) -> int:
    """
    Return a(n) mod 1e9 for n in [0,15], using:
      - exact shortcut for n < 8,
      - a(8+m) = H_{ω^3}(a(m)) = f^{a(m)+1}(a(m)) for m < 8.
    """
    if n < 8:
        return a0_7[n]  # already exact, << 1e9
    x0 = a0_7[n - 8]
    iters = x0 + 1
    r5 = _f2_iter_mod5(x0, iters)
    r2 = _f2_iter_mod2(x0, iters)
    return _crt_1e9(r2, r5)


def solve() -> int:
    # Exact a(n) for n=0..7
    a0_7 = [_a_exact_upto7(n) for n in range(8)]

    # Given test values from the problem statement:
    # G(n) = a(n) - 2
    assert a0_7[2] - 2 == 3
    assert a0_7[4] - 2 == 21
    assert a0_7[6] - 2 == 381
    assert sum(a0_7[n] - 2 for n in range(1, 8)) == 2517

    # Compute a(n) mod 1e9 for n=0..15
    a_mods = [_a_mod(n, a0_7) for n in range(16)]

    total = 0
    for n in range(1, 16):
        total = (total + (a_mods[n] - 2)) % MOD
    return total


if __name__ == "__main__":
    ans = solve()
    # Print as 9 digits (the problem asks for the last 9 digits).
    print(f"{ans:09d}")
