#!/usr/bin/env python3
"""
Project Euler 677: Coloured Graphs

We count (unlabelled) trees whose vertices are coloured {R,B,Y}, with:
- max degree: R<=4, B<=3, Y<=3
- no edge Y--Y

Let g(n) be the number of such trees with n vertices.
We compute g(10000) mod 1_000_000_007.

Key ideas:
- Ordinary generating functions (OGFs) for unlabelled rooted trees via Pólya cycle indices
  for SET_m with m <= 4 (bounded degree makes it finite).
- Dissymmetry theorem for trees:
    Unrooted = Vertex-rooted + Edge-rooted - Directed-edge-rooted
- Use "planted" trees (root has a parent edge) to build edge-rooted objects cleanly.

No external libraries.
"""

MOD = 1_000_000_007
INV2 = (MOD + 1) // 2
INV6 = pow(6, MOD - 2, MOD)
INV24 = pow(24, MOD - 2, MOD)


def _coeff_square(seq, d):
    """Coefficient of x^d in (seq(x))^2, assuming seq[0]=0. O(d)."""
    if d < 2:
        return 0
    half = d // 2
    s = 0
    if d & 1:
        # d odd: 2*sum_{i=1..half} a[i]*a[d-i]
        for i in range(1, half + 1):
            s += 2 * seq[i] * seq[d - i]
    else:
        # d even: a[half]^2 + 2*sum_{i=1..half-1} a[i]*a[d-i]
        mid = seq[half]
        s = mid * mid
        for i in range(1, half):
            s += 2 * seq[i] * seq[d - i]
    return s % MOD


def _compute_planted(N):
    """
    Compute planted (root has a parent edge) series up to N:
      PR[n], PB[n], PY[n] = planted trees of size n with root colour R,B,Y.
    Also return:
      A[n] = total planted trees size n = PR+PB+PY
      B[n] = planted trees size n whose root is non-yellow (R or B) = PR+PB
    And their squares-by-degree arrays up to N-1:
      sqA[d] = coeff x^d in A(x)^2 for d<=N-1
      sqB[d] = coeff x^d in B(x)^2 for d<=N-1
    """
    pr = [0] * (N + 1)
    pb = [0] * (N + 1)
    py = [0] * (N + 1)

    # A: all planted trees; B: planted trees with non-yellow root (R or B)
    a = [0] * (N + 1)
    b = [0] * (N + 1)

    # Squares needed in the recurrence (only degrees 0..N-1 are needed while building).
    sqA = [0] * (N + 1)
    sqB = [0] * (N + 1)

    for n in range(1, N + 1):
        d = n - 1  # we need coeff of degree d in the "children multiset" OGF

        # --- sqA[d] and sqB[d] (using symmetry to halve work) ---
        if d < 2:
            sqa = 0
            sqb = 0
        else:
            half = d // 2

            # sqA[d]
            s = 0
            if d & 1:
                for i in range(1, half + 1):
                    s += 2 * a[i] * a[d - i]
            else:
                mid = a[half]
                s = mid * mid
                for i in range(1, half):
                    s += 2 * a[i] * a[d - i]
            sqa = s % MOD

            # sqB[d]
            s = 0
            if d & 1:
                for i in range(1, half + 1):
                    s += 2 * b[i] * b[d - i]
            else:
                mid = b[half]
                s = mid * mid
                for i in range(1, half):
                    s += 2 * b[i] * b[d - i]
            sqb = s % MOD

        sqA[d] = sqa
        sqB[d] = sqb

        # --- cube coefficient of A^3 at degree d: sum_{i=1..d-1} a[i] * sqA[d-i] ---
        if d < 3:
            cube = 0
        else:
            s = 0
            # local bindings help a bit in CPython
            aa = a
            sqa_arr = sqA
            for i in range(1, d):
                s += aa[i] * sqa_arr[d - i]
            cube = s % MOD

        # --- prod coefficient of A(x)*A(x^2) at degree d ---
        # A(x^2) has coefficient a[j] at degree 2j.
        if d < 3:
            prod = 0
        else:
            s = 0
            aa = a
            for j in range(1, d // 2 + 1):
                i = d - 2 * j
                if i <= 0:
                    break
                s += aa[i] * aa[j]
            prod = s % MOD

        # --- F2_total[d] = 1 + A + SET_2(A) (truncated at size 2 multiset) ---
        f2 = a[d] + (1 if d == 0 else 0)
        tmp = sqa + (a[d // 2] if (d & 1) == 0 else 0)
        f2 = (f2 + (tmp % MOD) * INV2) % MOD

        # --- F2_nonY[d] (children can only be from B = PR+PB) ---
        f2n = b[d] + (1 if d == 0 else 0)
        tmp = sqb + (b[d // 2] if (d & 1) == 0 else 0)
        f2n = (f2n + (tmp % MOD) * INV2) % MOD

        # --- SET_3(A) term at degree d ---
        # SET_3 cycle index: (A1^3 + 3 A1 A2 + 2 A3) / 6
        t3 = (cube + 3 * prod) % MOD
        if d % 3 == 0:
            t3 = (t3 + 2 * a[d // 3]) % MOD
        t3 = (t3 * INV6) % MOD

        f3 = (f2 + t3) % MOD

        # Planted roots degree limits:
        # - red: max children 3 -> F3
        # - blue: max children 2 -> F2
        # - yellow: max children 2 and no yellow children -> F2_nonY
        pr[n] = f3
        pb[n] = f2
        py[n] = f2n

        bn = (f3 + f2) % MOD
        b[n] = bn
        a[n] = (bn + f2n) % MOD

    return pr, pb, py, a, b, sqA, sqB


def _f3_nony_at_degree(d, n, b, sqB, py):
    """
    Compute coeff of degree d in F3_nonY (used for yellow vertex-rooted trees),
    where children are drawn from B = planted trees with non-yellow root.

    F3 = F2 + SET_3.
    We already have F2 coefficient as py[n] (since PY[n] = x * F2_nonY at degree d).
    """
    f2n = py[n]
    if d < 3:
        return f2n

    # cube of B at degree d: sum_{i=1..d-1} b[i] * sqB[d-i]
    s = 0
    bb = b
    sqb_arr = sqB
    for i in range(1, d):
        s += bb[i] * sqb_arr[d - i]
    cube = s % MOD

    # prod B(x) * B(x^2) at degree d
    s = 0
    for j in range(1, d // 2 + 1):
        i = d - 2 * j
        if i <= 0:
            break
        s += bb[i] * bb[j]
    prod = s % MOD

    t3 = (cube + 3 * prod) % MOD
    if d % 3 == 0:
        t3 = (t3 + 2 * bb[d // 3]) % MOD
    t3 = (t3 * INV6) % MOD

    return (f2n + t3) % MOD


def _set4_total_at_degree(d, a, sqA):
    """
    Compute coeff of degree d in SET_4(A) where A is the allowed children class.

    Cycle index for SET_4:
      (A1^4 + 6 A1^2 A2 + 3 A2^2 + 8 A1 A3 + 6 A4) / 24
    with Ak = A(x^k).

    Here A is the planted-total series.
    """
    if d < 4:
        return 0

    # A1^4 term: coeff of degree d in (A^2)^2, i.e., (sqA)^2.
    # Use symmetry like a square.
    half = d // 2
    s = 0
    if d & 1:
        for i in range(1, half + 1):
            s += 2 * sqA[i] * sqA[d - i]
    else:
        mid = sqA[half]
        s = mid * mid
        for i in range(1, half):
            s += 2 * sqA[i] * sqA[d - i]
    a1_4 = s % MOD

    # A1^2 A2 term: coeff of A^2 * A(x^2).
    # A(x^2) has coefficient a[k] at degree 2k.
    s = 0
    aa = a
    sqa_arr = sqA
    for k in range(1, d // 2 + 1):
        s += sqa_arr[d - 2 * k] * aa[k]
    a1_2_a2 = s % MOD

    # A2^2 term: (A(x^2))^2 = (A^2)(x^2)
    a2_2 = sqa_arr[d // 2] if (d & 1) == 0 else 0

    # A1 A3 term: coeff of A * A(x^3)
    s = 0
    for k in range(1, d // 3 + 1):
        s += aa[d - 3 * k] * aa[k]
    a1_a3 = s % MOD

    # A4 term: A(x^4)
    a4 = aa[d // 4] if d % 4 == 0 else 0

    term = (a1_4 + 6 * a1_2_a2 + 3 * a2_2 + 8 * a1_a3 + 6 * a4) % MOD
    return (term * INV24) % MOD


def g(n, pr, pb, py, a, b, sqA, sqB):
    """Compute g(n) mod MOD using dissymmetry theorem and on-demand coefficients."""
    d = n - 1

    # Vertex-rooted:
    f3_total = pr[n]  # coefficient of F3_total at degree d
    f4_total = (f3_total + _set4_total_at_degree(d, a, sqA)) % MOD
    f3_nony = _f3_nony_at_degree(d, n, b, sqB, py)
    V = (f4_total + f3_total + f3_nony) % MOD

    # Edge-rooted (directed & undirected) need A^2 and PY^2 at degree n.
    # A^2 at degree n is sqA[n] if available, else compute on-demand.
    sqA_n = sqA[n] if sqA[n] else _coeff_square(a, n)
    sqPY_n = _coeff_square(py, n)

    A2_n = a[n // 2] if (n & 1) == 0 else 0  # A(x^2) at degree n
    PY2_n = py[n // 2] if (n & 1) == 0 else 0  # PY(x^2) at degree n

    # Directed-edge-rooted: ordered pair of planted endpoints, excluding Y-Y
    D = (sqA_n - sqPY_n) % MOD

    # Undirected-edge-rooted: unordered pair (cycle index of C2), excluding Y-Y
    E = ((sqA_n + A2_n - sqPY_n - PY2_n) % MOD) * INV2 % MOD

    # Dissymmetry theorem for trees
    return (V + E - D) % MOD


def solve(N=10_000):
    pr, pb, py, a, b, sqA, sqB = _compute_planted(N)

    # For the final g(N) we need sqA[N] (degree N in A^2); compute it once.
    sqA[N] = _coeff_square(a, N)

    # Test values from the problem statement
    assert g(2, pr, pb, py, a, b, sqA, sqB) == 5
    assert g(3, pr, pb, py, a, b, sqA, sqB) == 15
    assert g(4, pr, pb, py, a, b, sqA, sqB) == 57
    assert g(10, pr, pb, py, a, b, sqA, sqB) == 710249
    assert g(100, pr, pb, py, a, b, sqA, sqB) == 919747298

    return g(N, pr, pb, py, a, b, sqA, sqB)


if __name__ == "__main__":
    print(solve())
