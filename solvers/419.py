#!/usr/bin/env python3
"""
Project Euler 419: Look and Say Sequence

Compute A(n), B(n), C(n) = counts of digits 1,2,3 in the n-th term of the
look-and-say sequence that starts with "1", for n = 10^12, modulo 2^30.

No external libraries are used.
"""

MOD = 1 << 30
MASK = MOD - 1
TARGET_N = 10**12

# Conway's 92 "audioactive" elements (common elements only).
# Format per line: SYMBOL  SEQUENCE  DECAYS_INTO (dot-separated symbols)
#
# Source of the table: Wikipedia "Look-and-say sequence" article, section
# "Cosmological decay" (92 common elements; transuranics omitted).
ELEMENTS_DATA = """
H 22 H
He 13112221133211322112211213322112 Hf.Pa.H.Ca.Li
Li 312211322212221121123222112 He
Be 111312211312113221133211322112211213322112 Ge.Ca.Li
B 1321132122211322212221121123222112 Be
C 3113112211322112211213322112 B
N 111312212221121123222112 C
O 132112211213322112 N
F 31121123222112 O
Ne 111213322112 F
Na 123222112 Ne
Mg 3113322112 Pm.Na
Al 1113222112 Mg
Si 1322112 Al
P 311311222112 Ho.Si
S 1113122112 P
Cl 132112 S
Ar 3112 Cl
K 1112 Ar
Ca 12 K
Sc 3113112221133112 Ho.Pa.H.Ca.Co
Ti 11131221131112 Sc
V 13211312 Ti
Cr 31132 V
Mn 111311222112 Cr.Si
Fe 13122112 Mn
Co 32112 Fe
Ni 11133112 Zn.Co
Cu 131112 Ni
Zn 312 Cu
Ga 13221133122211332 Eu.Ca.Ac.H.Ca.Zn
Ge 31131122211311122113222 Ho.Ga
As 11131221131211322113322112 Ge.Na
Se 13211321222113222112 As
Br 3113112211322112 Se
Kr 11131221222112 Br
Rb 1321122112 Kr
Sr 3112112 Rb
Y 1112133 Sr.U
Zr 12322211331222113112211 Y.H.Ca.Tc
Nb 1113122113322113111221131221 Er.Zr
Mo 13211322211312113211 Nb
Tc 311322113212221 Mo
Ru 132211331222113112211 Eu.Ca.Tc
Rh 311311222113111221131221 Ho.Ru
Pd 111312211312113211 Rh
Ag 132113212221 Pd
Cd 3113112211 Ag
In 11131221 Cd
Sn 13211 In
Sb 3112221 Pm.Sn
Te 1322113312211 Eu.Ca.Sb
I 311311222113111221 Ho.Te
Xe 11131221131211 I
Cs 13211321 Xe
Ba 311311 Cs
La 11131 Ba
Ce 1321133112 La.H.Ca.Co
Pr 31131112 Ce
Nd 111312 Pr
Pm 132 Nd
Sm 311332 Pm.Ca.Zn
Eu 1113222 Sm
Gd 13221133112 Eu.Ca.Co
Tb 3113112221131112 Ho.Gd
Dy 111312211312 Tb
Ho 1321132 Dy
Er 311311222 Ho.Pm
Tm 11131221133112 Er.Ca.Co
Yb 1321131112 Tm
Lu 311312 Yb
Hf 11132 Lu
Ta 13112221133211322112211213322113 Hf.Pa.H.Ca.W
W 312211322212221121123222113 Ta
Re 111312211312113221133211322112211213322113 Ge.Ca.W
Os 1321132122211322212221121123222113 Re
Ir 3113112211322112211213322113 Os
Pt 111312212221121123222113 Ir
Au 132112211213322113 Pt
Hg 31121123222113 Au
Tl 111213322113 Hg
Pb 123222113 Tl
Bi 3113322113 Pm.Pb
Po 1113222113 Bi
At 1322113 Po
Rn 311311222113 Ho.At
Fr 1113122113 Rn
Ra 132113 Fr
Ac 3113 Ra
Th 1113 Ac
Pa 13 Th
U 3 Pa
""".strip()


def look_and_say(s: str) -> str:
    """One look-and-say step (run-length encoding with count then digit)."""
    out = []
    i = 0
    n = len(s)
    while i < n:
        j = i + 1
        ch = s[i]
        while j < n and s[j] == ch:
            j += 1
        out.append(str(j - i))
        out.append(ch)
        i = j
    return "".join(out)


def parse_elements():
    rows = []
    for line in ELEMENTS_DATA.splitlines():
        sym, seq, decay = line.split()
        rows.append((sym, seq, decay))
    if len(rows) != 92:
        raise ValueError(f"Expected 92 elements, got {len(rows)}")
    return rows


def build_tables(rows):
    sym_to_idx = {sym: i for i, (sym, _, _) in enumerate(rows)}
    seqs = [seq for _, seq, _ in rows]
    decays = [[sym_to_idx[s] for s in decay.split(".")] for _, _, decay in rows]
    digit_counts = [(seq.count("1"), seq.count("2"), seq.count("3")) for seq in seqs]

    # Candidates for decomposition keyed by first digit
    start_map = {"1": [], "2": [], "3": []}
    for i, seq in enumerate(seqs):
        start_map[seq[0]].append(i)
    # Try longer matches first (usually helps DP reach the end quickly)
    for k in start_map:
        start_map[k].sort(key=lambda i: len(seqs[i]), reverse=True)

    return sym_to_idx, seqs, decays, digit_counts, start_map


def decompose_into_elements(s: str, seqs, start_map):
    """
    Split s into a concatenation of element sequences (Conway atoms).
    Returns a count vector of length 92, or None if decomposition fails.
    """
    L = len(s)
    prev_pos = [-1] * (L + 1)
    prev_atom = [-1] * (L + 1)
    prev_pos[0] = 0

    for pos in range(L):
        if prev_pos[pos] == -1:
            continue
        c = s[pos]
        for ai in start_map.get(c, ()):
            seq = seqs[ai]
            if s.startswith(seq, pos):
                nxt = pos + len(seq)
                if prev_pos[nxt] == -1:
                    prev_pos[nxt] = pos
                    prev_atom[nxt] = ai

    if prev_pos[L] == -1:
        return None

    counts = [0] * 92
    pos = L
    while pos > 0:
        ai = prev_atom[pos]
        counts[ai] += 1
        pos = prev_pos[pos]
    return counts


def build_transition_matrix(decays):
    """
    Dense 92x92 matrix M where M[i][j] = how many times element j appears
    in the decay of element i (one look-and-say step, then re-splitting).
    """
    n = 92
    M = [[0] * n for _ in range(n)]
    for i, prod in enumerate(decays):
        row = M[i]
        for j in prod:
            row[j] += 1
    return M


def mat_mul(A, B):
    """Dense matrix multiplication modulo 2^30 (via bitmask)."""
    n = 92
    rng = range(n)
    mask = MASK
    res = [[0] * n for _ in range(n)]
    for i in rng:
        Ai = A[i]
        Ri = res[i]
        for k, aik in enumerate(Ai):
            if aik:
                Bk = B[k]
                # Ri[j] += aik * Bk[j]
                for j in rng:
                    Ri[j] += aik * Bk[j]
        for j in rng:
            Ri[j] &= mask
    return res


def vec_mul(v, M):
    """Row-vector times dense matrix modulo 2^30 (via bitmask)."""
    n = 92
    rng = range(n)
    mask = MASK
    res = [0] * n
    for i, vi in enumerate(v):
        if vi:
            Mi = M[i]
            for j in rng:
                res[j] += vi * Mi[j]
    for j in rng:
        res[j] &= mask
    return res


def pow_apply_vec(v, M, exp):
    """Compute v * (M^exp) modulo 2^30 using binary exponentiation."""
    while exp > 0:
        if exp & 1:
            v = vec_mul(v, M)
        exp >>= 1
        if exp:
            M = mat_mul(M, M)
    return v


def counts_from_vec(v, digit_counts):
    """Convert element-count vector to (A,B,C) digit counts modulo 2^30."""
    a = b = c = 0
    for i, vi in enumerate(v):
        if vi:
            da, db, dc = digit_counts[i]
            a += vi * da
            b += vi * db
            c += vi * dc
    return a & MASK, b & MASK, c & MASK


def solve(n: int):
    rows = parse_elements()
    _, seqs, decays, digit_counts, start_map = build_tables(rows)
    M = build_transition_matrix(decays)

    # Find the earliest term that can be decomposed into Conway's 92 elements.
    term = "1"
    n0 = 1
    v0 = None
    for step in range(1, 200):
        comp = decompose_into_elements(term, seqs, start_map)
        if comp is not None:
            n0 = step
            v0 = comp
            break
        term = look_and_say(term)
    if v0 is None:
        raise RuntimeError("Failed to find a decomposable term (unexpected).")

    if n < n0:
        # For very small n, just brute-force the string (tiny).
        s = "1"
        for _ in range(n - 1):
            s = look_and_say(s)
        return s.count("1"), s.count("2"), s.count("3")

    v = pow_apply_vec(v0, M, n - n0)
    return counts_from_vec(v, digit_counts)


def main():
    # Problem statement check:
    assert solve(40) == (31254, 20259, 11625)

    a, b, c = solve(TARGET_N)
    print(f"{a},{b},{c}")


if __name__ == "__main__":
    main()
