#!/usr/bin/env python3
"""
Project Euler 300: Protein Folding (no third-party dependencies)

We model proteins as length-n strings of hydrophobic (H) and polar (P) residues.
A folding is a self-avoiding walk on the 2D square lattice.

A H–H "contact point" is counted whenever two H residues occupy adjacent
lattice cells. (The Project Euler check for n=8 implies that contacts between
consecutive residues are INCLUDED.)

Task:
For each of the 2^n proteins, find the maximum possible number of H–H contacts
over all foldings, then average those maxima.

This implementation:
- Enumerates distinct non-consecutive contact maps (bitmasks) of SAWs with
  symmetry reduction.
- Uses bit-sliced arithmetic on big integers to evaluate all 2^n proteins in
  parallel, without NumPy.
"""

from __future__ import annotations

from typing import List


def frac_over_power_of_two_to_decimal(numerator: int, n: int) -> str:
    """Convert numerator / 2^n to an exact terminating decimal string."""
    # numerator / 2^n = numerator * 5^n / 10^n
    scaled = numerator * pow(5, n)
    denom = pow(10, n)
    int_part = scaled // denom
    frac_part = scaled % denom
    s = f"{int_part}.{frac_part:0{n}d}".rstrip("0")
    return s[:-1] if s.endswith(".") else s


def generate_contact_maps(n: int) -> List[int]:
    """
    Enumerate all distinct non-consecutive contact maps for self-avoiding walks
    of length n-1 on the square lattice.

    A contact map is stored as a bitmask over all residue pairs (i,j), i<j,
    in the same order as nested loops for i<j. We exclude consecutive pairs
    (|i-j|=1) because those adjacencies always exist in any folding.
    """
    # Pair indexing (i<j) -> bit index in [0..n*(n-1)/2-1]
    pair_idx = [[-1] * n for _ in range(n)]
    p = 0
    for i in range(n):
        for j in range(i + 1, n):
            pair_idx[i][j] = p
            p += 1

    # Coordinate packing for fast neighbor key arithmetic
    OFF = 64
    SHIFT = 7
    STEP_X = 1 << SHIFT  # adding this increments x by +1 in packed space

    def key(x: int, y: int) -> int:
        return ((x + OFF) << SHIFT) | (y + OFF)

    # Symmetry reduction:
    # fix residue 0 at (0,0), residue 1 at (1,0) => removes rotations
    # require final y >= 0 => removes mirror duplicates across x-axis
    occ = {key(0, 0): 0, key(1, 0): 1}
    maps: set[int] = set()

    def dfs(k: int, x: int, y: int, contact_mask: int) -> None:
        if k == n - 1:
            if y >= 0 and contact_mask != 0:
                maps.add(contact_mask)
            return

        nxt = k + 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            nk = key(nx, ny)
            if nk in occ:
                continue

            occ[nk] = nxt
            new_mask = contact_mask

            # Only new contacts involving residue `nxt` can appear.
            for adjk in (nk + STEP_X, nk - STEP_X, nk + 1, nk - 1):
                j = occ.get(adjk)
                if j is None or abs(j - nxt) == 1:
                    continue
                a, b = (j, nxt) if j < nxt else (nxt, j)
                new_mask |= 1 << pair_idx[a][b]

            dfs(nxt, nx, ny, new_mask)
            del occ[nk]

    dfs(1, 1, 0, 0)
    return list(maps)


def _bitset_P_positions(n: int, i: int) -> int:
    """
    Return an integer bitset S of length 2^n such that:
      bit p of S == 1  iff  protein p has P at position i  (i.e., (p>>i)&1 == 1)

    This is built in O(1) big-int ops via a repeated-bit-pattern formula.
    """
    M = 1 << n
    L = 1 << i  # run length
    W = 2 * L  # pattern width
    U = ((1 << L) - 1) << L  # lower L zeros, upper L ones
    r = M // W  # repeats
    series = ((1 << (r * W)) - 1) // ((1 << W) - 1)  # 1 + 2^W + ... + 2^{(r-1)W}
    return U * series


def _sum_bitsets(bitsets: List[int], bits: int) -> List[int]:
    """
    Bit-sliced sum of many {0,1} bitsets.

    Returns slices s[0..bits-1] (LSB to MSB) such that for each position p,
    the binary number formed by bits of s is equal to the count of input
    bitsets that had bit p set.
    """
    slices = [0] * bits
    for S in bitsets:
        carry = S
        for b in range(bits):
            new = slices[b] ^ carry
            carry = slices[b] & carry
            slices[b] = new
            if carry == 0:
                break
    return slices


def _add_slices(A: List[int], B: List[int], bits: int) -> List[int]:
    """Bit-sliced addition: C = A + B (per position), returning `bits` slices."""
    carry = 0
    res = [0] * bits
    for k in range(bits):
        ai = A[k] if k < len(A) else 0
        bi = B[k] if k < len(B) else 0
        res[k] = ai ^ bi ^ carry
        carry = (ai & bi) | (ai & carry) | (bi & carry)
    return res


def _max_slices(A: List[int], B: List[int], bits: int, mask_all: int) -> List[int]:
    """
    Bit-sliced max: C = max(A, B) per position, returning `bits` slices.
    """
    gt = 0
    eq = mask_all
    for k in range(bits - 1, -1, -1):
        ai = A[k] if k < len(A) else 0
        bi = B[k] if k < len(B) else 0
        gt |= eq & bi & (mask_all ^ ai)  # bi & ~ai
        eq &= mask_all ^ (ai ^ bi)  # ~(ai^bi)
    not_gt = mask_all ^ gt

    res = [0] * bits
    for k in range(bits):
        ai = A[k] if k < len(A) else 0
        bi = B[k] if k < len(B) else 0
        res[k] = (ai & not_gt) | (bi & gt)
    return res


def _decode_bits(x: int) -> List[int]:
    """Return list of set-bit indices in x (lsb->msb)."""
    out: List[int] = []
    while x:
        lsb = x & -x
        out.append(lsb.bit_length() - 1)
        x ^= lsb
    return out


def total_optimal_contacts(n: int) -> int:
    """
    Return sum over all 2^n proteins of (maximum H–H contacts over all foldings).
    Proteins are represented as n-bit integers where bit=1 means P, bit=0 means H.
    """
    contact_maps = generate_contact_maps(n)
    max_edges = max((m.bit_count() for m in contact_maps), default=0)

    bits_direct = max(1, (n - 1).bit_length())
    bits_contact = max(1, max_edges.bit_length())  # count range 0..max_edges
    bits_total = max(1, (n - 1 + max_edges).bit_length())

    M = 1 << n
    mask_all = (1 << M) - 1

    # Pbits[i] has a 1 at protein p iff residue i is P in protein p
    Pbits = [_bitset_P_positions(n, i) for i in range(n)]

    # Pair bitsets in the same i<j order as the generator's pair_idx.
    # bothH(i,j) is 1 at p iff both residues are H in protein p.
    pair_bitsets: List[int] = []
    for i in range(n):
        for j in range(i + 1, n):
            pair_bitsets.append(mask_all & ~(Pbits[i] | Pbits[j]))

    # Consecutive pairs always adjacent in the chain; they count in every folding.
    consec: List[int] = []
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1:
                consec.append(pair_bitsets[idx])
            idx += 1

    direct_slices = _sum_bitsets(consec, bits_direct)
    direct_ext = direct_slices + [0] * (bits_total - len(direct_slices))

    # Best starts as the always-present consecutive H-H contacts
    best = direct_ext[:]

    # For each contact map, compute total = direct + (nonconsecutive contacts)
    for cm in contact_maps:
        edges = _decode_bits(cm)  # <= 8 edges for n=15
        contact_slices = _sum_bitsets([pair_bitsets[e] for e in edges], bits_contact)
        total = _add_slices(direct_ext, contact_slices, bits_total)
        best = _max_slices(best, total, bits_total, mask_all)

    # Sum best scores over all proteins by summing popcounts of bit-slices.
    numerator = 0
    for k in range(bits_total):
        numerator += (1 << k) * best[k].bit_count()
    return numerator


def solve(n: int = 15) -> str:
    """Return the exact average as a decimal string."""
    total = total_optimal_contacts(n)
    return frac_over_power_of_two_to_decimal(total, n)


def _self_test() -> None:
    # From the Project Euler statement:
    # average for n=8 is 850 / 2^8 = 3.3203125
    assert total_optimal_contacts(8) == 850
    assert solve(8) == "3.3203125"


if __name__ == "__main__":
    _self_test()
    print(solve(15))
