#!/usr/bin/env python3
"""
Project Euler 655
How many positive palindromes < 10^32 are divisible by 10,000,019?

Constraints:
- Pure Python, no external libraries.

Approach (high level):
- A length-L palindrome is determined by k = ceil(L/2) digits d[0..k-1],
  where d[i] is used at positions i and L-1-i (except the middle digit for odd L).
- The palindrome value modulo MOD is a linear combination of these digits:
      sum d[i] * w[i] ≡ 0 (mod MOD)
  for precomputable weights w[i].
- For k <= 14: meet-in-the-middle over at most 7 digits per side (<= 10^7 iterations).
- For k >= 15 (L=29..32): a bit-sliced ("bitplane") method counts 4-digit-block pair-sums
  without enumerating 10^8 pairs, using big integer bitsets + cyclic rotations + bitwise add.

The code also includes asserts for the small test facts stated in the problem statement
(for divisor 109). Those tests are brute-forced.
"""

from array import array

MOD = 10_000_019


# -----------------------------
# Helpers for statement asserts
# -----------------------------


def _is_palindrome(n: int) -> bool:
    s = str(n)
    return s == s[::-1]


def _brute_first_k_palindromes_divisible_by(divisor: int, k: int, start: int = 1):
    out = []
    n = start
    while len(out) < k:
        if n % divisor == 0 and _is_palindrome(n):
            out.append(n)
        n += 1
    return out


def _brute_count_positive_palindromes_below(limit: int, divisor: int) -> int:
    # "positive palindromes", so start from 1 (exclude 0)
    cnt = 0
    for n in range(1, limit):
        if n % divisor == 0 and _is_palindrome(n):
            cnt += 1
    return cnt


def run_problem_statement_asserts() -> None:
    # From the statement (divisor 109):
    first3 = _brute_first_k_palindromes_divisible_by(109, 3, start=1)
    assert first3 == [545, 5995, 15151], first3

    cnt = _brute_count_positive_palindromes_below(100_000, 109)
    assert cnt == 9, cnt


# -----------------------------
# Core math: weights for length
# -----------------------------


def _pow10_mod_upto(n: int) -> list[int]:
    p = [1] * (n + 1)
    for i in range(1, n + 1):
        p[i] = (p[i - 1] * 10) % MOD
    return p


_POW10 = _pow10_mod_upto(31)  # enough for L up to 32


def weights_for_length(L: int) -> list[int]:
    """
    Returns weights w[0..k-1] for length L, where k = ceil(L/2), such that
    palindrome divisible by MOD <=> sum d[i]*w[i] ≡ 0 (mod MOD),
    with digit constraint d[0] in 1..9 (leading digit), others 0..9.
    """
    k = (L + 1) // 2
    w = [0] * k
    for i in range(k):
        if (L % 2 == 1) and (i == k - 1):
            # middle digit appears once
            w[i] = _POW10[i]
        else:
            w[i] = (_POW10[i] + _POW10[L - 1 - i]) % MOD
    return w


# -----------------------------
# Meet-in-the-middle for k<=14
# -----------------------------


def _build_contrib(weights_slice: list[int]) -> list[int]:
    """Contribution table for all base-10 numbers of length len(weights_slice) (little-endian digits)."""
    length = len(weights_slice)
    if length == 0:
        return [0]
    size = 10**length
    out = [0] * size
    for v in range(size):
        x = v
        s = 0
        for j in range(length):
            d = x % 10
            x //= 10
            s += d * weights_slice[j]
        out[v] = s % MOD
    return out


def _count_mitm(weights: list[int]) -> int:
    """
    Count digit assignments d[0..k-1] with d0 in 1..9 and others 0..9
    such that sum d[i]*weights[i] ≡ 0 (mod MOD), using meet-in-the-middle.
    Valid for k<=14 (we choose a split with each side <=7 digits).
    """
    k = len(weights)
    if k == 0:
        return 0
    if k == 1:
        # d0 in 1..9, need d0*w0 ≡0 mod MOD. Since MOD is prime and w0 != 0 mod MOD, impossible.
        return 0

    # Split into A = digits [0..m-1] and B = digits [m..k-1]
    m = k // 2  # for k<=14 => m<=7 and k-m<=7
    lenA = m
    lenB = k - m

    # Build contribution tables for A using a 3-digit low chunk + remaining high chunk
    loA = min(3, lenA)
    hiA = lenA - loA
    contribA_lo = _build_contrib(weights[0:loA])
    contribA_hi = _build_contrib(weights[loA:lenA]) if hiA > 0 else [0]

    # Restrict digit0 (the units digit of the whole palindrome) to be nonzero:
    # digit0 is within the low chunk of A (since A starts at index 0).
    if loA >= 1:
        allowedA_lo = [v for v in range(10**loA) if (v % 10) != 0]
    else:
        # Shouldn't happen because lenA>=1 when k>=2 and m>=1
        allowedA_lo = [0]

    combosA = len(allowedA_lo) * (10**hiA)
    use_array = combosA >= 2_500_000  # only really triggers when lenA==7

    if use_array:
        freq = array("I", [0]) * MOD
    else:
        freq = {}

    # Fill frequency table for A
    if use_array:
        freq_arr = freq
        for hi in range(10**hiA):
            base = contribA_hi[hi]
            for lo in allowedA_lo:
                s = base + contribA_lo[lo]
                if s >= MOD:
                    s -= MOD
                freq_arr[s] += 1
    else:
        freq_dict = freq
        get = freq_dict.get
        for hi in range(10**hiA):
            base = contribA_hi[hi]
            for lo in allowedA_lo:
                s = base + contribA_lo[lo]
                if s >= MOD:
                    s -= MOD
                freq_dict[s] = get(s, 0) + 1

    # Enumerate B sums and accumulate matches
    loB = min(3, lenB)
    hiB = lenB - loB
    offsetB = lenA
    contribB_lo = _build_contrib(weights[offsetB : offsetB + loB])
    contribB_hi = (
        _build_contrib(weights[offsetB + loB : offsetB + lenB]) if hiB > 0 else [0]
    )
    sizeB_lo = 10**loB
    sizeB_hi = 10**hiB

    total = 0
    if use_array:
        freq_arr = freq
        for hi in range(sizeB_hi):
            base = contribB_hi[hi]
            for lo in range(sizeB_lo):
                s = base + contribB_lo[lo]
                if s >= MOD:
                    s -= MOD
                t = 0 if s == 0 else (MOD - s)
                total += freq_arr[t]
    else:
        freq_dict = freq
        get = freq_dict.get
        for hi in range(sizeB_hi):
            base = contribB_hi[hi]
            for lo in range(sizeB_lo):
                s = base + contribB_lo[lo]
                if s >= MOD:
                    s -= MOD
                t = 0 if s == 0 else (MOD - s)
                total += get(t, 0)

    return total


# -----------------------------
# Bit-sliced method for k>=15
# -----------------------------


def _group_residues(
    weights: list[int], start: int, length: int, restrict_d0: bool
) -> list[int]:
    """
    Enumerate residues for all digit combinations in a contiguous digit group.
    Digits are little-endian within the group.
    If restrict_d0 is True, the very first digit (d0) must be 1..9.
    This only makes sense when start == 0 and digit0 is in this group.
    """
    size = 10**length
    out: list[int] = []
    for v in range(size):
        if restrict_d0 and (v % 10 == 0):
            continue
        x = v
        s = 0
        for j in range(length):
            d = x % 10
            x //= 10
            s += d * weights[start + j]
        out.append(s % MOD)
    return out


def _planes_from_residues(residues: list[int], bytes_len: int) -> list[int]:
    """
    Build bitplanes for the per-residue multiplicity of `residues`.
    plane[b] has bit r set iff the b-th bit of count[r] is 1.
    Planes are returned as Python ints of length MOD bits.
    """
    counts: dict[int, int] = {}
    get = counts.get
    for r in residues:
        counts[r] = get(r, 0) + 1

    maxc = 0
    for c in counts.values():
        if c > maxc:
            maxc = c

    bits = maxc.bit_length()
    if bits == 0:
        return []

    bas = [bytearray(bytes_len) for _ in range(bits)]
    for r, c in counts.items():
        b = 0
        idx = r >> 3
        mask = 1 << (r & 7)
        while c:
            if c & 1:
                bas[b][idx] |= mask
            c >>= 1
            b += 1

    return [int.from_bytes(ba, "little") for ba in bas]


def _rotate_left_bits(x: int, shift: int, bitlen: int, mask: int) -> int:
    """Rotate x (bitlen bits) left by shift (mod bitlen)."""
    if shift == 0:
        return x
    return ((x << shift) & mask) | (x >> (bitlen - shift))


def _add_bitset_into_planes(
    planes: list[int], bits_to_add: int, start_bit: int
) -> None:
    """
    Add bits_to_add (a bitset meaning +1 at those positions) into the bit-sliced integer
    stored in `planes`, starting at bit position `start_bit` (i.e. adding (bits_to_add << start_bit)).
    """
    i = start_bit
    carry = bits_to_add
    while carry:
        if i == len(planes):
            planes.append(0)
        cur = planes[i]
        s = cur ^ carry
        carry = cur & carry
        planes[i] = s
        i += 1


def _pair_sum_distribution_bitplanes(
    A_res: list[int], B_planes: list[int], bitlen: int, mask: int
) -> list[int]:
    """
    Compute distribution of sums a+b (mod MOD) where a ranges over A_res (with multiplicity)
    and b is the multiset described by B_planes. Result is returned as bitplanes.
    """
    out: list[int] = []
    for a in A_res:
        sh = a  # shift by residue value
        for bit_idx, plane in enumerate(B_planes):
            if plane:
                shifted = _rotate_left_bits(plane, sh, bitlen, mask)
                _add_bitset_into_planes(out, shifted, bit_idx)
    return out


def _dot_bitplanes(A_planes: list[int], B_planes: list[int]) -> int:
    """
    Given two per-residue count arrays encoded as bitplanes, compute:
        sum_r A[r] * B[r]
    exactly, using bitset AND + popcount over planes.
    """
    total = 0
    for i, Ai in enumerate(A_planes):
        if not Ai:
            continue
        for j, Bj in enumerate(B_planes):
            if not Bj:
                continue
            total += (Ai & Bj).bit_count() << (i + j)
    return total


def _count_large_k(weights: list[int]) -> int:
    """
    For k=15 or 16, count solutions using 4-digit block pairing with a bit-sliced convolution.
    """
    k = len(weights)
    # Group sizes: 4,4,4,remaining (3 or 4)
    g0_len = 4
    g1_len = 4
    g2_len = 4
    g3_len = k - 12
    if g3_len <= 0:
        raise ValueError("k too small for _count_large_k")

    g0 = _group_residues(weights, 0, g0_len, restrict_d0=True)
    g1 = _group_residues(weights, 4, g1_len, restrict_d0=False)
    g2 = _group_residues(weights, 8, g2_len, restrict_d0=False)
    g3 = _group_residues(weights, 12, g3_len, restrict_d0=False)

    # Build bitplanes for g1.
    bitlen = MOD
    bytes_len = (bitlen + 7) // 8
    mask = (1 << bitlen) - 1

    g1_planes = _planes_from_residues(g1, bytes_len)
    left_planes = _pair_sum_distribution_bitplanes(g0, g1_planes, bitlen, mask)

    # For the right side, we build the distribution of NEGATED sums:
    # right_store[t] = #pairs with (-(a+b) mod MOD) == t
    # by negating group residues first and then doing the same pair sum.
    g2n = [0 if r == 0 else (MOD - r) for r in g2]
    g3n = [0 if r == 0 else (MOD - r) for r in g3]

    g3_planes = _planes_from_residues(g3n, bytes_len)
    right_planes = _pair_sum_distribution_bitplanes(g2n, g3_planes, bitlen, mask)

    # Total quadruples with sum ≡ 0 is dot(left, right_neg_sums)
    return _dot_bitplanes(left_planes, right_planes)


# -----------------------------
# Solve full Euler instance
# -----------------------------


def count_length(L: int) -> int:
    w = weights_for_length(L)
    k = len(w)
    if k <= 14:
        return _count_mitm(w)
    return _count_large_k(w)


def solve() -> int:
    total = 0
    for L in range(1, 33):
        total += count_length(L)
    return total


def main() -> None:
    run_problem_statement_asserts()
    print(solve())


if __name__ == "__main__":
    main()
